package org.outerj.daisy.diff;

import java.io.BufferedReader;
import java.io.ByteArrayInputStream;
import java.io.ByteArrayOutputStream;
import java.io.IOException;
import java.io.InputStream;
import java.io.InputStreamReader;
import java.io.OutputStream;
import java.io.UnsupportedEncodingException;
import java.net.InetSocketAddress;
import java.net.URLDecoder;
import java.util.HashMap;
import java.util.Locale;
import java.util.StringTokenizer;
import java.util.concurrent.Executors;

import javax.xml.transform.TransformerFactory;
import javax.xml.transform.sax.SAXTransformerFactory;
import javax.xml.transform.sax.TransformerHandler;
import javax.xml.transform.stream.StreamResult;

import org.outerj.daisy.diff.html.HTMLDiffer;
import org.outerj.daisy.diff.html.HtmlSaxDiffOutput;
import org.outerj.daisy.diff.html.SideBySideHTMLDiffer;
import org.outerj.daisy.diff.html.TextNodeComparator;
import org.outerj.daisy.diff.html.dom.DomTreeBuilder;
import org.xml.sax.ContentHandler;
import org.xml.sax.InputSource;
import org.xml.sax.helpers.AttributesImpl;

import com.sun.net.httpserver.Headers;
import com.sun.net.httpserver.HttpExchange;
import com.sun.net.httpserver.HttpHandler;
import com.sun.net.httpserver.HttpServer;

public class DaisyDiffServer {
	private static int port = 8080;

	public static void main(String[] args) throws IOException {
		for (int i = 0; i < args.length; i++) {
			String[] split = args[i].split("=");
			if (split[0].equalsIgnoreCase("--port")) {
				port = Integer.parseInt(split[1]);
			}
		}
		InetSocketAddress addr = new InetSocketAddress(port);
		HttpServer server = HttpServer.create(addr, 0);

		server.createContext("/", new DaisyDiffHandler());
		server.setExecutor(Executors.newCachedThreadPool());
		server.start();
		System.out.println("Server is listening on port " + port);
	}
}

class DaisyDiffHandler extends FormHandler {

	public String doGet(HashMap<String, String> form, String path) {
		this.contentType = "text/plain";

		return "Server is up.  Use POST method to request a diff or merge.";
	}

	public String doPost(HashMap<String, String> form, String path) {
		this.contentType = "text/html";

		StringBuffer response = new StringBuffer();
		if (path.equals("/diff")) {
			if (form.containsKey("field1") && form.containsKey("field2")) {
				response.append(diff(form.get("field1"), form.get("field2")));
			} else {
				response.append("Required POST parameters: field1, field2");
			}
		} else if (path.equals("/merge")) {
			if (form.containsKey("field1") && form.containsKey("field2")
					&& form.containsKey("ancestor")) {
				response.append(merge(form.get("field1"), form.get("field2"),
						form.get("ancestor")));
			} else {
				response.append("Required POST parameters: field1, field2, ancestor");
			}
		}

		return response.toString();
	}

	private String merge(String left, String right, String ancestor) {
		try {

			ByteArrayOutputStream out = new ByteArrayOutputStream();
			SAXTransformerFactory tf = (SAXTransformerFactory) TransformerFactory
					.newInstance();
			TransformerHandler result = tf.newTransformerHandler();
			result.setResult(new StreamResult(out));

			XslFilter filter = new XslFilter();
			String xsl = "org/outerj/daisy/diff/threeway.xsl";
			ContentHandler postProcess = filter.xsl(result, xsl);

			Locale locale = Locale.getDefault();
			String prefix = "diff";

			HtmlCleaner cleaner = new HtmlCleaner();

			InputSource ancestorSource = new InputSource(
					new ByteArrayInputStream(ancestor.getBytes()));
			InputSource oldSource = new InputSource(new ByteArrayInputStream(
					left.getBytes()));
			InputSource newSource = new InputSource(new ByteArrayInputStream(
					right.getBytes()));

			DomTreeBuilder ancestorHandler = new DomTreeBuilder();
			cleaner.cleanAndParse(ancestorSource, ancestorHandler);
			TextNodeComparator ancestorComparator = new TextNodeComparator(
					ancestorHandler, locale, true);

			DomTreeBuilder oldHandler = new DomTreeBuilder();
			cleaner.cleanAndParse(oldSource, oldHandler);
			TextNodeComparator leftComparator = new TextNodeComparator(
					oldHandler, locale, true);

			DomTreeBuilder newHandler = new DomTreeBuilder();
			cleaner.cleanAndParse(newSource, newHandler);
			TextNodeComparator rightComparator = new TextNodeComparator(
					newHandler, locale, true);

			postProcess.startDocument();
			postProcess.startElement("", "diffreport", "diffreport",
					new AttributesImpl());
			postProcess.startElement("", "diff", "diff", new AttributesImpl());
			HtmlSaxDiffOutput output = new HtmlSaxDiffOutput(postProcess,
					prefix);

			HTMLDiffer differ = new HTMLDiffer(output);
			differ.diff(ancestorComparator, leftComparator, rightComparator);

			postProcess.endElement("", "diff", "diff");
			postProcess.endElement("", "diffreport", "diffreport");
			postProcess.endDocument();

			return out.toString();

		} catch (Throwable e) {
			return e.getMessage();
		}
	}

	private String diff(String left, String right) {
		try {
			ByteArrayOutputStream out = new ByteArrayOutputStream();
			SAXTransformerFactory tf = (SAXTransformerFactory) TransformerFactory
					.newInstance();
			TransformerHandler result = tf.newTransformerHandler();
			result.setResult(new StreamResult(out));

			XslFilter filter = new XslFilter();

			String xsl = "org/outerj/daisy/diff/sidebyside.xsl";

			ContentHandler postProcess = filter.xsl(result, xsl);

			Locale locale = Locale.getDefault();
			String prefix = "diff";

			HtmlCleaner cleaner = new HtmlCleaner();

			InputSource oldSource = new InputSource(new ByteArrayInputStream(
					left.getBytes()));
			InputSource newSource = new InputSource(new ByteArrayInputStream(
					right.getBytes()));

			DomTreeBuilder oldHandler = new DomTreeBuilder();
			cleaner.cleanAndParse(oldSource, oldHandler);

			TextNodeComparator leftComparator = new TextNodeComparator(
					oldHandler, locale);

			DomTreeBuilder newHandler = new DomTreeBuilder();
			cleaner.cleanAndParse(newSource, newHandler);

			TextNodeComparator rightComparator = new TextNodeComparator(
					newHandler, locale);

			postProcess.startDocument();
			postProcess.startElement("", "diffreport", "diffreport",
					new AttributesImpl());

			postProcess.startElement("", "diff", "diff", new AttributesImpl());
			HtmlSaxDiffOutput output = new HtmlSaxDiffOutput(postProcess,
					prefix);

			SideBySideHTMLDiffer differ = new SideBySideHTMLDiffer(output);
			differ.diff(leftComparator, rightComparator);

			postProcess.endElement("", "diff", "diff");
			postProcess.endElement("", "diffreport", "diffreport");
			postProcess.endDocument();

			return out.toString();

		} catch (Throwable e) {
			return e.getMessage();
		}

	}
}

abstract class FormHandler implements HttpHandler {
	protected String contentType = "text/plain";

	public void handle(HttpExchange exchange) throws IOException {

		StringBuffer content = new StringBuffer();
		BufferedReader br = new BufferedReader(new InputStreamReader(exchange
				.getRequestBody()));
		String line;
		while ((line = br.readLine()) != null) {
			content.append(line);
		}
		br.close();

		HashMap<String, String> form = parseForm(content.toString(), "UTF-8");

		String requestMethod = exchange.getRequestMethod();
		String path = exchange.getRequestURI().getPath();
		System.out.println(requestMethod + " " + path);
		
		String response;

		if (requestMethod.equalsIgnoreCase("GET")) {
			response = doGet(form, path);
		} else if (requestMethod.equalsIgnoreCase("POST")) {
			response = doPost(form, path);
		} else {
			response = "Method not supported: " + requestMethod;
		}
		sendResponseHeaders(exchange, response.length());
		OutputStream responseBody = exchange.getResponseBody();
		responseBody.write(response.getBytes());
		responseBody.close();
		System.out.println(response.length() + " bytes sent in response");
	}

	private HashMap<String, String> parseForm(String raw, String encoding)
			throws UnsupportedEncodingException {
		HashMap<String, String> form = new HashMap<String, String>();
		StringTokenizer params = new StringTokenizer(raw, "&");

		while (params.hasMoreTokens()) {
			String p = params.nextToken();
			String[] parts = p.split("=");
			form.put(URLDecoder.decode(parts[0], encoding), URLDecoder.decode(
					parts[1], encoding));
		}
		return form;
	}

	private void sendResponseHeaders(HttpExchange exchange, int length)
			throws IOException {
		Headers responseHeaders = exchange.getResponseHeaders();
		responseHeaders.set("Content-Type", contentType);
		exchange.sendResponseHeaders(200, length);
	}

	public abstract String doGet(HashMap<String, String> form, String path);

	public abstract String doPost(HashMap<String, String> form, String path);
}
