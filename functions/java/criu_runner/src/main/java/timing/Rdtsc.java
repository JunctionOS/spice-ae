package timing;

public class Rdtsc {
    static {
        System.loadLibrary("rdtsc"); // Load the shared library
    }

    public native long get_rdtsc();
}
