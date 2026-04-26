package matmul;

import org.json.JSONObject;
import java.util.Random;

public class Matmul {
    private static final int N = 200;
    private int[][] a;
    private int[][] b;

    public Matmul() {
        Random rand = new Random();

        this.a = new int[N][N];
        this.b = new int[N][N];
        for (int i = 0; i < N; i += 1) {
            for (int j = 0; j < N; j += 1) {
                this.a[i][j] = rand.nextInt(10);
                this.b[i][j] = rand.nextInt(10);
            }
        }
    }

    public void handler(JSONObject args) {
        for (int i = 0; i < N; i += 1) {
            for (int j = 0; j < N; j += 1) {
                int res_i_j = 0;
                for (int k = 0; k < N; k += 1) {
                    res_i_j += a[i][k] * a[k][j];
                }
                b[i][j] = res_i_j;
            }
        }
    }
}
