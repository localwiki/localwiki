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
	private static  int port = 8080;

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

	public String doGet(HashMap<String, String> form) {
		this.contentType = "text/plain";
		
		return "Server is up.  Use POST method to request a diff.";
	}

	public String doPost(HashMap<String, String> form) {
		this.contentType = "text/html";
		
		StringBuffer response = new StringBuffer();

		if (form.containsKey("field1") && form.containsKey("field2")) {
			response.append(diff(form.get("field1"), form.get("field2")));
		} else {
			response.append("Required POST parameters: field1, field2");
		}

		return response.toString();
	}

	private String diff(String left, String right)
	{
		try{
			ByteArrayOutputStream out = new ByteArrayOutputStream();

			SAXTransformerFactory tf = (SAXTransformerFactory) TransformerFactory
			.newInstance();

			TransformerHandler result = tf.newTransformerHandler();

			result.setResult(new StreamResult(out));

			InputStream oldStream, newStream;

			XslFilter filter = new XslFilter();

			String xsl = "org/outerj/daisy/diff/sidebyside.xsl"; 

			ContentHandler postProcess = filter.xsl(result, xsl);

			Locale locale = Locale.getDefault();
			String prefix = "diff";

			HtmlCleaner cleaner = new HtmlCleaner();

			InputSource oldSource = new InputSource(new ByteArrayInputStream(left.getBytes()));
			InputSource newSource = new InputSource(new ByteArrayInputStream(right.getBytes()));

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
			
			postProcess.startElement("", "diff", "diff",
					new AttributesImpl());
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

		HashMap<String, String> form = parseForm(content.toString(), "UTF-8");

		String requestMethod = exchange.getRequestMethod();
		String response;

		if (requestMethod.equalsIgnoreCase("GET")) {
			response = doGet(form);
		} else if (requestMethod.equalsIgnoreCase("POST")) {
			response = doPost(form);
		} else {
			response = "Method not supported";
		}
		
		sendResponseHeaders(exchange);
		OutputStream responseBody = exchange.getResponseBody();
		System.out.println(response.length() + " bytes sent in response");
		responseBody.write(response.getBytes());
		responseBody.close();
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

	private void sendResponseHeaders(HttpExchange exchange) throws IOException {
		Headers responseHeaders = exchange.getResponseHeaders();
		responseHeaders.set("Content-Type", contentType);
		exchange.sendResponseHeaders(200, 0);
	}

	public abstract String doGet(HashMap<String, String> form);

	public abstract String doPost(HashMap<String, String> form);
}
