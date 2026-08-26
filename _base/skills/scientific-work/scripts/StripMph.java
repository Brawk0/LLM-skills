import com.comsol.model.Model;
import com.comsol.model.util.ModelUtil;
import java.io.File;

/**
 * Strip a COMSOL model down to what is worth keeping: geometry, materials, physics, mesh
 * settings, study and solver settings, results definitions.  Throw away what a re-run
 * reproduces: solution data, mesh data, derived tables, and the model's edit history.
 *
 * The point is not disk space for its own sake.  A model that lives only on one PC is a model
 * that will be lost, and the honest way to keep it is to put it where the notes are - which
 * means it has to be small enough that syncing it is not a burden.  A solved three-dimensional
 * model runs to hundreds of megabytes; the same model without its solution is a few.
 *
 * Driven by environment variables so nothing has to be recompiled per file:
 *   MPH_IN    input model
 *   MPH_OUT   output model (defaults to <input>_stripped.mph)
 *   MPH_KEEP  comma-separated list of things to KEEP: "mesh", "tables", "hist"
 *
 * Every clearing step is attempted separately and reported, because these operations are named
 * differently across COMSOL versions and one unrecognised call must not abort the whole strip.
 * No anonymous inner classes: `comsolcompile` emits only the top-level class file, so a model
 * script that uses them fails at run time with "Error running java class - Detail: Foo$1".
 */
public class StripMph {

    public static void main(String[] args) throws Exception {
        String in = env("MPH_IN", null);
        if (in == null) {
            System.out.println("STRIP ERROR: set MPH_IN");
            return;
        }
        String keep = env("MPH_KEEP", "").toLowerCase();
        String out = env("MPH_OUT", in.replaceAll("(?i)\\.mph$", "") + "_stripped.mph");

        File fin = new File(in);
        long before = fin.length();
        System.out.println("STRIP IN  " + fin.getAbsolutePath() + "  " + mb(before));

        Model model = ModelUtil.load("stripme", fin.getAbsolutePath());
        int cleared = 0;

        try {
            String[] sols = model.sol().tags();
            for (int i = 0; i < sols.length; i++) {
                cleared += clearOneSolution(model, sols[i]);
            }
        } catch (Throwable t) {
            System.out.println("  solutions unavailable: " + t.getClass().getSimpleName());
        }

        if (!keep.contains("mesh")) {
            try {
                String[] comps = model.component().tags();
                for (int i = 0; i < comps.length; i++) {
                    String[] meshes = model.component(comps[i]).mesh().tags();
                    for (int j = 0; j < meshes.length; j++) {
                        try {
                            model.component(comps[i]).mesh(meshes[j]).clearMesh();
                            System.out.println("  cleared mesh " + comps[i] + "/" + meshes[j]);
                            cleared++;
                        } catch (Throwable t) {
                            System.out.println("  skipped mesh " + comps[i] + "/" + meshes[j]
                                    + " (" + t.getClass().getSimpleName() + ")");
                        }
                    }
                }
            } catch (Throwable t) {
                System.out.println("  meshes unavailable: " + t.getClass().getSimpleName());
            }
        }

        if (!keep.contains("tables")) {
            try {
                String[] tabs = model.result().table().tags();
                for (int i = 0; i < tabs.length; i++) {
                    try {
                        model.result().table(tabs[i]).clearTableData();
                        System.out.println("  cleared table " + tabs[i]);
                        cleared++;
                    } catch (Throwable t) {
                        System.out.println("  skipped table " + tabs[i]
                                + " (" + t.getClass().getSimpleName() + ")");
                    }
                }
            } catch (Throwable t) {
                System.out.println("  tables unavailable: " + t.getClass().getSimpleName());
            }
        }

        if (!keep.contains("hist")) {
            try {
                model.resetHist();
                System.out.println("  cleared history");
                cleared++;
            } catch (Throwable t) {
                System.out.println("  skipped history (" + t.getClass().getSimpleName() + ")");
            }
        }

        File fout = new File(out);
        model.save(fout.getAbsolutePath());
        ModelUtil.remove("stripme");

        long after = fout.length();
        System.out.println("STRIP OUT " + fout.getAbsolutePath() + "  " + mb(after) + "  ("
                + String.format("%.1f", 100.0 * after / Math.max(before, 1L))
                + " % of original, " + cleared + " items cleared)");
    }

    /** Two spellings exist across versions; try the newer one first. */
    private static int clearOneSolution(Model model, String tag) {
        try {
            model.sol(tag).clearSolutionData();
            System.out.println("  cleared solution " + tag);
            return 1;
        } catch (Throwable t) {
            try {
                model.sol(tag).clearSolution();
                System.out.println("  cleared solution " + tag + " (legacy call)");
                return 1;
            } catch (Throwable t2) {
                System.out.println("  skipped solution " + tag
                        + " (" + t2.getClass().getSimpleName() + ")");
                return 0;
            }
        }
    }

    private static String mb(long bytes) {
        return String.format("%.1f MB", bytes / 1048576.0);
    }

    private static String env(String k, String d) {
        String v = System.getenv(k);
        return (v == null || v.trim().length() == 0) ? d : v.trim();
    }
}
