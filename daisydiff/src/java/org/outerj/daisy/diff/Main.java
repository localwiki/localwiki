package org.outerj.daisy.diff;

import java.io.BufferedReader;
import java.io.File;
import java.io.FileInputStream;
import java.io.InputStream;
import java.io.InputStreamReader;
import java.net.URI;
import java.net.URISyntaxException;
import java.util.Locale;

import javax.xml.transform.TransformerFactory;
import javax.xml.transform.sax.SAXTransformerFactory;
import javax.xml.transform.sax.TransformerHandler;
import javax.xml.transform.stream.StreamResult;

import org.outerj.daisy.diff.html.HTMLDiffer;
import org.outerj.daisy.diff.html.HtmlSaxDiffOutput;
import org.outerj.daisy.diff.html.TextNodeComparator;
import org.outerj.daisy.diff.html.dom.DomTreeBuilder;
import org.xml.sax.ContentHandler;
import org.xml.sax.InputSource;
import org.xml.sax.SAXException;
import org.xml.sax.helpers.AttributesImpl;

public class Main {
  static boolean quietMode = false;
  
    public static void main(String[] args) throws URISyntaxException {

        if (args.length < 2)
            help();

        boolean htmlDiff = true;
        boolean htmlOut = true;
        String outputFile = "daisydiff.htm";
        String[] css = new String[]{};
        
        try {
            for (int i = 2; i < args.length; i++) {
                String[] split = args[i].split("=");
                if (split[0].equalsIgnoreCase("--file")) {
                    outputFile = split[1];
                } else if (split[0].equalsIgnoreCase("--type")) {
                    if (split[1].equalsIgnoreCase("tag")) {
                        htmlDiff = false;
                    }
                } else if (split[0].equalsIgnoreCase("--css")) {
                    css = split[1].split(";");
                } else if (split[0].equalsIgnoreCase("--output")) {
                    if (split[1].equalsIgnoreCase("xml")) {
                        htmlOut = false;
                    }
                } else if (split[0].equals("--q")){
                  quietMode = true;
                } else{
                    help();
                }

            }
            if (!quietMode){
              System.out.println("            ______________");
              System.out.println("           /Daisy Diff 1.0\\");
              System.out.println("          /________________\\");
              System.out.println();
              System.out.println(" -= http://code.google.com/p/daisydiff/ =-");
              System.out.println("");
              System.out.println();
              System.out.println("Comparing documents:");
              System.out.println("  " + args[0]);
              System.out.println("and");
              System.out.println("  " + args[1]);
              System.out.println();
              if (htmlDiff)
                System.out.println("Diff type: html");
              else
                System.out.println("Diff type: tag");
              System.out.println("Writing "+(htmlOut?"html":"xml")+" output to " + outputFile);
            }


            if(css.length>0){
                if (!quietMode)
                  System.out.println("Adding external css files:");
                for(String cssLink:css){
                    System.out.println("  "+cssLink);
                }
            }
            if (!quietMode){
              System.out.println("");
              System.out.print(".");
            }
            SAXTransformerFactory tf = (SAXTransformerFactory) TransformerFactory
                    .newInstance();

            TransformerHandler result = tf.newTransformerHandler();
            result.setResult(new StreamResult(new File(outputFile)));
            
            InputStream oldStream, newStream;
            
            if (args[0].startsWith("http://")) {
                oldStream = new URI(args[0]).toURL().openStream();
            }
            else {
                oldStream = new FileInputStream(args[0]);
            }
            if (args[1].startsWith("http://")) {
                newStream = new URI(args[1]).toURL().openStream();
            }
            else {
                newStream = new FileInputStream(args[1]);
            }

            XslFilter filter = new XslFilter();

            if (htmlDiff) {

                ContentHandler postProcess = htmlOut? filter.xsl(result,
                        "org/outerj/daisy/diff/htmlheader.xsl"):result;

                Locale locale = Locale.getDefault();
                String prefix = "diff";

                HtmlCleaner cleaner = new HtmlCleaner();

                InputSource oldSource = new InputSource(oldStream);
                InputSource newSource = new InputSource(newStream);

                DomTreeBuilder oldHandler = new DomTreeBuilder();
                cleaner.cleanAndParse(oldSource, oldHandler);
                System.out.print(".");
                TextNodeComparator leftComparator = new TextNodeComparator(
                        oldHandler, locale);

                DomTreeBuilder newHandler = new DomTreeBuilder();
                cleaner.cleanAndParse(newSource, newHandler);
                System.out.print(".");
                TextNodeComparator rightComparator = new TextNodeComparator(
                        newHandler, locale);

                postProcess.startDocument();
                postProcess.startElement("", "diffreport", "diffreport",
                        new AttributesImpl());
                doCSS(css, postProcess);
                postProcess.startElement("", "diff", "diff",
                        new AttributesImpl());
                HtmlSaxDiffOutput output = new HtmlSaxDiffOutput(postProcess,
                        prefix);
                
                HTMLDiffer differ = new HTMLDiffer(output);
                differ.diff(leftComparator, rightComparator);
                System.out.print(".");
                postProcess.endElement("", "diff", "diff");
                postProcess.endElement("", "diffreport", "diffreport");
                postProcess.endDocument();

            } else {

                ContentHandler postProcess = htmlOut? filter.xsl(result,
                        "org/outerj/daisy/diff/tagheader.xsl"):result;
                postProcess.startDocument();
                postProcess.startElement("", "diffreport", "diffreport",
                        new AttributesImpl());
                postProcess.startElement("", "diff", "diff",
                        new AttributesImpl());
                System.out.print(".");
                DaisyDiff.diffTag(new BufferedReader(new InputStreamReader(
                        oldStream)), new BufferedReader(new InputStreamReader(
                        newStream)), postProcess);
                System.out.print(".");
                postProcess.endElement("", "diff", "diff");
                postProcess.endElement("", "diffreport", "diffreport");
                postProcess.endDocument();
            }

        } catch (Throwable e) {
          if (quietMode){
            System.out.println(e);
          } else {
            e.printStackTrace();
            if (e.getCause() != null) {
                e.getCause().printStackTrace();
            }
            if (e instanceof SAXException) {
                ((SAXException) e).getException().printStackTrace();
            }
            help();
          }
        }
        if (quietMode)
          System.out.println();
        else
          System.out.println("done");

    }

    private static void doCSS(String[] css, ContentHandler handler) throws SAXException {
        handler.startElement("", "css", "css",
                new AttributesImpl());
        for(String cssLink : css){
            AttributesImpl attr = new AttributesImpl();
            attr.addAttribute("", "href", "href", "CDATA", cssLink);
            attr.addAttribute("", "type", "type", "CDATA", "text/css");
            attr.addAttribute("", "rel", "rel", "CDATA", "stylesheet");
            handler.startElement("", "link", "link",
                    attr);
            handler.endElement("", "link", "link");
        }
        
        handler.endElement("", "css", "css");
        
    }

    private static void help() {
        System.out.println("==========================");
        System.out.println("DAISY DIFF HELP:");
        System.out.println("java -jar daisydiff.jar [oldHTML] [newHTML]");
        System.out
                .println("--file=[filename] - Write output to the specified file.");
        System.out
                .println("--type=[html/tag] - Use the html (default) diff algorithm or the tag diff.");
        System.out.println("--css=[cssfile1;cssfile2;cssfile3] - Add external CSS files.");
        System.out.println("--output=[html/xml] - Write html (default) or xml output.");
        System.out.println("--q  - Generate less console output.");
        System.out.println("");
        System.out.println("EXAMPLES: ");
        System.out.println("(1)");
        System.out
                .println("java -jar daisydiff.jar http://web.archive.org/web/20070107145418/http://news.bbc.co.uk/ http://web.archive.org/web/20070107182640/http://news.bbc.co.uk/ --css=http://web.archive.org/web/20070107145418/http://news.bbc.co.uk/nol/shared/css/news_r5.css");
        System.out.println("(2)");
        System.out.println("java -jar daisydiff.jar http://cocoondev.org/wiki/291-cd/version/15/part/SimpleDocumentContent/data http://cocoondev.org/wiki/291-cd/version/17/part/SimpleDocumentContent/data --css=http://cocoondev.org/resources/skins/daisysite/css/daisy.css --output=xml --file=daisysite.htm");
        System.out.println("==========================");
        System.exit(0);
    }

}
