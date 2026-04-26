import org.json.JSONObject;
import java.lang.reflect.Method;
import java.nio.file.Paths;
import java.util.ArrayList;
import java.util.List;
import timing.Rdtsc;

public class CRIURunner {

    static final int WARMUP_ITERS = 10;

    public static String toCamelCase(String snake) {
        StringBuilder result = new StringBuilder();

        String[] parts = snake.split("_");

        for (int i = 0; i < parts.length; i++) {
            String part = parts[i];
            if (!part.isEmpty()) {
                result.append(part.substring(0, 1).toUpperCase());
                result.append(part.substring(1));
            }
        }

        return result.toString();
    }

    public static void main(String[] args) throws Exception {
        if (args.length != 2) {
            System.err.println("Usage: java Runner <program> <json_string>");
            System.exit(1);
        }

        Rdtsc clock = new Rdtsc();

        String prog = args[0];
        String jsonStr = args[1];

        if (prog.equals("chameleon") || prog.equals("pyaes")) {
            prog += "1";
        }

        String className = prog + "." + toCamelCase(prog);
        Class<?> targetClass = Class.forName(className);
        Method method = targetClass.getMethod("handler", JSONObject.class);
        Object instance = targetClass.getDeclaredConstructor().newInstance();

        JSONObject json = new JSONObject(jsonStr);
        List<Long> warmupCycles = new ArrayList<>();

        for (int i = 0; i < WARMUP_ITERS; i++) {
            long start = clock.get_rdtsc();
            Object result = method.invoke(instance, json);
            long end = clock.get_rdtsc();
            System.out.println(result);
            warmupCycles.add(end - start);
        }

        System.out.flush();
        System.out.println("looping");
        System.out.flush();

        long now = System.currentTimeMillis();
        while (System.currentTimeMillis() - now < 10000) {
            // spin for 10 seconds
        }

        System.out.println("done looping");
        System.out.flush();

        long start = clock.get_rdtsc();
        method.invoke(instance, json);
        long end = clock.get_rdtsc();
        long cold = end - start;

        JSONObject result = new JSONObject();
        result.put("warmup", warmupCycles);
        result.put("cold", cold);
        result.put("program", args[0]);
        System.out.println("DATA " + result.toString());

        System.out.println("iteration finish: " + clock.get_rdtsc());
        System.exit(0);
    }

    private static String capitalize(String s) {
        if (s.length() == 0) return s;
        return Character.toUpperCase(s.charAt(0)) + s.substring(1);
    }
}
