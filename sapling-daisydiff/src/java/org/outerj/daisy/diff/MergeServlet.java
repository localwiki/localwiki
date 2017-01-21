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

public class MergeServlet extends HttpServlet
{
    protected void doGet(HttpServletRequest req, HttpServletResponse resp)
        throws ServletException, IOException
    {
    	doPost(req, resp);
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
    	resp.setContentType( "text/xml; charset=UTF-8" );
        PrintWriter out = resp.getWriter();

        String left = req.getParameter("field1");
        String right = req.getParameter("field2");
        String ancestor = req.getParameter("ancestor");
        if(left == null || right == null || ancestor == null)
        {
        	out.println("<html>");
            out.println("<body>");
            out.println("Required POST parameters: field1, field2, ancestor");
            out.println("</body>");
            out.println("</html>");
        }
        else{
        	out.println(merge(left, right, ancestor));
        }
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
}