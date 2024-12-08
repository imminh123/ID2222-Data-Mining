package se.kth.jabeja;

import org.apache.log4j.Logger;
import se.kth.jabeja.config.Config;
import se.kth.jabeja.config.NodeSelectionPolicy;
import se.kth.jabeja.io.FileIO;
import se.kth.jabeja.rand.RandNoGenerator;

import static java.lang.Math.pow;

import java.io.File;
import java.io.IOException;
import java.util.*;

public class Jabeja {
    final static Logger logger = Logger.getLogger(Jabeja.class);
    private final Config config;
    private final HashMap<Integer/* id */, Node/* neighbors */> entireGraph;
    private final List<Integer> nodeIds;
    private int numberOfSwaps;
    private int round;
    private float T;
    private boolean resultFileCreated = false;

    private boolean annealing = true;
    private boolean bonus = true;
    private Integer currentRound = 0;
    private Integer annealingRound = 0;

    // -------------------------------------------------------------------
    public Jabeja(HashMap<Integer, Node> graph, Config config) {
        this.entireGraph = graph;
        this.nodeIds = new ArrayList(entireGraph.keySet());
        this.round = 0;
        this.numberOfSwaps = 0;
        this.config = config;
        // Maximum initial temperature is 1 for annealing, else get the temperature from
        // the config
        this.T = this.annealing ? 1.0F : config.getTemperature();
    }

    // -------------------------------------------------------------------
    public void startJabeja() throws IOException {
        for (round = 0; round < config.getRounds(); round++) {
            for (int id : entireGraph.keySet()) {
                sampleAndSwap(id);
            }

            saCoolDown();
            report();
        }
    }

    /**
     * Simulated analealing cooling function
     */
    private void saCoolDown() {
        if (annealing) {
            // Cooling down during annealing
            final float MIN_T = 0.0001F;
            final int MAX_ROUNDS = 400;
            annealingRound++;

            // Update temperature
            T *= config.getDelta();

            // Ensure temperature doesn't go below the minimum
            if (T < MIN_T) {
                T = MIN_T;
            }

            // If temperature is at the minimum, increment round and check if max rounds are
            // reached
            if (T == MIN_T) {
                currentRound++;
                if (currentRound >= MAX_ROUNDS) {
                    // Reset temperature and rounds after max rounds
                    currentRound = 0;
                    annealingRound = 0;
                    T = 1;
                }
            }
        } else {
            if (T > 1)
                T -= config.getDelta();
            if (T < 1)
                T = 1;
        }
    }

    /**
     * Calculate the probability of accepting a new state.
     * Found in the paper "The Simulated Annealing Algorithm" by Katrina Ellison
     * Geltman
     * For bonus, the acceptance probability is an own implementation
     */
    private double acceptanceProbability(double oldCost, double newCost) {
        if (bonus) {
            return Math.exp((newCost - oldCost) / Math.pow(T, annealingRound));
        } else {
            return Math.exp((newCost - oldCost) / T);
        }
    }

    /**
     * Sample and swap algorith at node p
     * 
     * @param nodeId
     */
    private void sampleAndSwap(int nodeId) {
        Node partner = null;
        Node nodep = entireGraph.get(nodeId);

        if (config.getNodeSelectionPolicy() == NodeSelectionPolicy.HYBRID
                || config.getNodeSelectionPolicy() == NodeSelectionPolicy.LOCAL) {
            // swap with random neighbors
            partner = findPartner(nodeId, getNeighbors(nodep));
        }

        if (config.getNodeSelectionPolicy() == NodeSelectionPolicy.HYBRID
                || config.getNodeSelectionPolicy() == NodeSelectionPolicy.RANDOM) {
            // if local policy fails then randomly sample the entire graph
            if (partner == null) {
                partner = findPartner(nodeId, getSample(nodeId));
            }
        }

        // swap the colors
        if (partner != null) {
            int tempColor = partner.getColor();
            partner.setColor(nodep.getColor());
            nodep.setColor(tempColor);
            numberOfSwaps++;
        }
    }

    public Node findPartner(int nodeId, Integer[] nodes) {
        Node nodep = entireGraph.get(nodeId);
        Node bestPartner = null;
        double highestBenefit = 0;

        for (Integer id : nodes) {
            Node nodeq = entireGraph.get(id);

            // Compute old and new values
            double oldValue = calculateValue(nodep, nodep.getColor(), nodeq, nodeq.getColor());
            double newValue = calculateValue(nodep, nodeq.getColor(), nodeq, nodep.getColor());

            // Select partner based on annealing or direct comparison
            if (annealing) {
                double acceptanceProb = acceptanceProbability(oldValue, newValue);
                if (acceptPartner(oldValue, newValue, acceptanceProb, highestBenefit)) {
                    bestPartner = nodeq;
                    highestBenefit = acceptanceProb;
                }
            } else if (newValue * T > oldValue && newValue > highestBenefit) {
                bestPartner = nodeq;
                highestBenefit = newValue;
            }
        }
        return bestPartner;
    }

    // Compute value based on node degrees and color
    private double calculateValue(Node node1, int color1, Node node2, int color2) {
        int degree1 = getDegree(node1, color1);
        int degree2 = getDegree(node2, color2);
        return Math.pow(degree1, config.getAlpha()) + Math.pow(degree2, config.getAlpha());
    }

    // Decide whether to accept the partner during annealing
    private boolean acceptPartner(double oldValue, double newValue, double acceptanceProb, double highestBenefit) {
        Random random = new Random();
        double prob = random.nextDouble();
        return oldValue != newValue && acceptanceProb > prob && acceptanceProb > highestBenefit;
    }

    /**
     * The the degreee on the node based on color
     * 
     * @param node
     * @param colorId
     * @return how many neighbors of the node have color == colorId
     */
    private int getDegree(Node node, int colorId) {
        int degree = 0;
        for (int neighborId : node.getNeighbours()) {
            Node neighbor = entireGraph.get(neighborId);
            if (neighbor.getColor() == colorId) {
                degree++;
            }
        }
        return degree;
    }

    /**
     * Returns a uniformly random sample of the graph
     * 
     * @param currentNodeId
     * @return Returns a uniformly random sample of the graph
     */
    private Integer[] getSample(int currentNodeId) {
        int count = config.getUniformRandomSampleSize();
        int rndId;
        int size = entireGraph.size();
        ArrayList<Integer> rndIds = new ArrayList<Integer>();

        while (true) {
            rndId = nodeIds.get(RandNoGenerator.nextInt(size));
            if (rndId != currentNodeId && !rndIds.contains(rndId)) {
                rndIds.add(rndId);
                count--;
            }

            if (count == 0)
                break;
        }

        Integer[] ids = new Integer[rndIds.size()];
        return rndIds.toArray(ids);
    }

    /**
     * Get random neighbors. The number of random neighbors is controlled using
     * -closeByNeighbors command line argument which can be obtained from the config
     * using {@link Config#getRandomNeighborSampleSize()}
     * 
     * @param node
     * @return
     */
    private Integer[] getNeighbors(Node node) {
        ArrayList<Integer> list = node.getNeighbours();
        int count = config.getRandomNeighborSampleSize();
        int rndId;
        int index;
        int size = list.size();
        ArrayList<Integer> rndIds = new ArrayList<Integer>();

        if (size <= count)
            rndIds.addAll(list);
        else {
            while (true) {
                index = RandNoGenerator.nextInt(size);
                rndId = list.get(index);
                if (!rndIds.contains(rndId)) {
                    rndIds.add(rndId);
                    count--;
                }

                if (count == 0)
                    break;
            }
        }

        Integer[] arr = new Integer[rndIds.size()];
        return rndIds.toArray(arr);
    }

    /**
     * Generate a report which is stored in a file in the output dir.
     *
     * @throws IOException
     */
    private void report() throws IOException {
        int grayLinks = 0;
        int migrations = 0; // number of nodes that have changed the initial color
        int size = entireGraph.size();

        for (int i : entireGraph.keySet()) {
            Node node = entireGraph.get(i);
            int nodeColor = node.getColor();
            ArrayList<Integer> nodeNeighbours = node.getNeighbours();

            if (nodeColor != node.getInitColor()) {
                migrations++;
            }

            if (nodeNeighbours != null) {
                for (int n : nodeNeighbours) {
                    Node p = entireGraph.get(n);
                    int pColor = p.getColor();

                    if (nodeColor != pColor)
                        grayLinks++;
                }
            }
        }

        int edgeCut = grayLinks / 2;

        logger.info("round: " + round +
                ", edge cut:" + edgeCut +
                ", swaps: " + numberOfSwaps +
                ", migrations: " + migrations);

        saveToFile(edgeCut, migrations);
    }

    private void saveToFile(int edgeCuts, int migrations) throws IOException {
        String delimiter = "\t\t";
        String outputFilePath;

        // output file name
        File inputFile = new File(config.getGraphFilePath());
        outputFilePath = config.getOutputDir() +
                File.separator +
                inputFile.getName() + "_" +
                "NS" + "_" + config.getNodeSelectionPolicy() + "_" +
                "GICP" + "_" + config.getGraphInitialColorPolicy() + "_" +
                "T" + "_" + config.getTemperature() + "_" +
                "D" + "_" + config.getDelta() + "_" +
                "RNSS" + "_" + config.getRandomNeighborSampleSize() + "_" +
                "URSS" + "_" + config.getUniformRandomSampleSize() + "_" +
                "A" + "_" + config.getAlpha() + "_" +
                "R" + "_" + config.getRounds() + ".txt";

        if (!resultFileCreated) {
            File outputDir = new File(config.getOutputDir());
            if (!outputDir.exists()) {
                if (!outputDir.mkdir()) {
                    throw new IOException("Unable to create the output directory");
                }
            }
            // create folder and result file with header
            String header = "# Migration is number of nodes that have changed color.";
            header += "\n\nRound" + delimiter + "Edge-Cut" + delimiter + "Swaps" + delimiter + "Migrations" + delimiter
                    + "Skipped" + "\n";
            FileIO.write(header, outputFilePath);
            resultFileCreated = true;
        }

        FileIO.append(round + delimiter + (edgeCuts) + delimiter + numberOfSwaps + delimiter + migrations + "\n",
                outputFilePath);
    }
}