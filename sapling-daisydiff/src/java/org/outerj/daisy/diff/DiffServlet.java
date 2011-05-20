package org.outerj.daisy.diff;

import java.io.*;
import java.util.Locale;

import javax.servlet.*;
import javax.servlet.http.*;
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

public class DiffServlet extends HttpServlet
{
    protected void doGet(HttpServletRequest req, HttpServletResponse resp)
        throws ServletException, IOException
    {
        PrintWriter out = resp.getWriter();

        out.println("<html>");
        out.println("<body>");
        out.println("Please use POST");
        out.println("</body>");
        out.println("</html>");
    }

    protected void doPost(HttpServletRequest req, HttpServletResponse resp)
        throws ServletException, IOException
    {
    	resp.setContentType( "text/html; charset=UTF-8" );
        PrintWriter out = resp.getWriter();

        String left = req.getParameter("field1");
        String right = req.getParameter("field2");
        if(left == null || right == null)
        {
        	out.println("<html>");
            out.println("<body>");
            out.println("Required POST parameters: field1, field2");
            out.println("</body>");
            out.println("</html>");
        }
        else out.println(diff(left, right));
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