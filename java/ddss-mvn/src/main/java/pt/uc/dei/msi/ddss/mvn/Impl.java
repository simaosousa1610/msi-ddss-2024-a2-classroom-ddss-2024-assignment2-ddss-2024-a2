/**
 * =============================================
 * = Design and Development of Secure Software =
 * =============== MSI 2019/2020 ===============
 * ========== Practical Assignment #2 ==========
 * ================== Part #1 ==================
 * =============================================
 * =============================================
 * === Department of Informatics Engineering ===
 * =========== University of Coimbra ===========
 * =============================================
 * <p>
 * Prof. Marco Vieira <mvieira@dei.uc.pt>
 * Prof. Nuno Antunes <nmsa@dei.uc.pt>
 * <p>
 * <p>
 * Repository: https://github.com/msi-ddss/ddss2019
 */
package pt.uc.dei.msi.ddss.mvn;

import java.util.ArrayList;
import java.util.List;
import org.jtwig.JtwigModel;
import org.jtwig.JtwigTemplate;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import spark.Request;
import spark.Response;

/**
 * Important: these sources are merely suggestions of implementations. You
 * should modify everything you deem as necessary and be responsible for all the
 * content that is delivered.
 *
 *
 *
 * @author Nuno Antunes <nmsa@dei.uc.pt>
 */
public class Impl {

    private static final Logger LOGGER = LoggerFactory.getLogger(Impl.class);

    public static Object part1_vulnerable(Request req, Response res) {
        /* example on how to obtain posted values */
        String password = req.queryParams("v_password");
        String username = req.queryParams("v_username");
        String remember = req.queryParams("v_remember");

        LOGGER.info("v_password -> " + password);
        LOGGER.info("v_username -> " + username);
        LOGGER.info("v_remember -> " + remember);

        return "part1_vulnerable";
    }

    public static Object part1_correct(Request req, Response res) {
        /* example on how to obtain posted values */
        String password = req.queryParams("v_password");
        String username = req.queryParams("v_username");
        String remember = req.queryParams("v_remember");

        LOGGER.info("v_password -> " + password);
        LOGGER.info("v_username -> " + username);
        LOGGER.info("v_remember -> " + remember);

        return "part1_correct";
    }

    public static Object part2_vulnerable(Request req, Response res) {

        // this loads the template from src/main/resources
        JtwigTemplate part2 = JtwigTemplate.classpathTemplate("templates/part2.twig");

        List<String> list = new ArrayList<>();

        list.add("Message 1");
        list.add("Message 2");
        list.add("Message 3");
        list.add("Message 4");
        list.add("Message 5");
        list.add("Message 5");

        // this sets the value for the {{listOfMessages}} list, which is iterated with
        // a for loop
        JtwigModel model = JtwigModel.newModel().with("listOfMessages", list);

        // this sets the value for the {{username}} var
        model.with("username", "Andre and Jose");

        return part2.render(model);
    }

    public static Object part2_correct(Request req, Response res) {
        /**
         *
         * <p>
         * <p>
         * <p>
         * <p>
         */

        return "part2_correct";
    }

    public static Object part3_vulnerable(Request req, Response res) {
        /**
         *
         * <p>
         * <p>
         * <p>
         * <p>
         */

        return "part3_vulnerable";
    }

    public static Object part3_correct(Request req, Response res) {
        /**
         *
         * <p>
         * <p>
         * <p>
         * <p>
         */

        return "part3_correct";
    }
}
