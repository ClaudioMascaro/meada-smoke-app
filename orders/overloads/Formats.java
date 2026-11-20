package orders.overloads;

public class Formats {
    static String encode(String value) { return json(value); }
    static String encode(int value) { return number(value); }

    static String json(String value) { return "\"" + value + "\""; }
    static String number(int value) { return Integer.toString(value); }

    static String textOrder() { return encode("open"); }
    static String countOrders() { return encode(42); }
}
