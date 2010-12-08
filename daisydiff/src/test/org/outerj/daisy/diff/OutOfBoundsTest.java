/*
 * Copyright 2009 Guy Van den Broeck
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *     http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */
package org.outerj.daisy.diff;
import java.io.StringReader;
import java.util.Locale;

import org.junit.Test;
import org.xml.sax.InputSource;
import org.xml.sax.helpers.DefaultHandler;

/**
 * Test for regressions involving out of bounds exceptions
 * 
 * @author guy
 *
 */
public class OutOfBoundsTest  {

	@Test
    public void testOutOfBounds1() throws Exception {
        
        String html1 = "<html><body>var v2</body></html>";
        String html2 = "<html>  \n  <body>  \n  Hello world  \n  </body>  \n  </html>";
    
        DaisyDiff.diffHTML(new InputSource(new StringReader(html1)), new InputSource(new StringReader(html2)), new DefaultHandler(), "test", Locale.ENGLISH);
        
    }
	@Test
    public void testOutOfBounds2() throws Exception {
        
        String html1 = "<html>  \n  <body>  \n  Hello world  \n  </body>  \n  </html>";
        String html2 = "<html><body>var v2</body></html>";
    
        DaisyDiff.diffHTML(new InputSource(new StringReader(html1)), new InputSource(new StringReader(html2)), new DefaultHandler(), "test", Locale.ENGLISH);
        
    }
	@Test
    public void testOutOfBounds3() throws Exception {
        
        String html1 = "<html><head></head><body><p>test</p></body></html>";
        String html2 = "<html><head></head><body></body></html>";
    
        DaisyDiff.diffHTML(new InputSource(new StringReader(html1)), new InputSource(new StringReader(html2)), new DefaultHandler(), "test", Locale.ENGLISH);
        
    }
	@Test
    public void testOutOfBounds4() throws Exception {
        
        String html1 = "<html><head></head><body></body></html>";
        String html2 = "<html><head></head><body><p>test</p></body></html>";
    
        DaisyDiff.diffHTML(new InputSource(new StringReader(html1)), new InputSource(new StringReader(html2)), new DefaultHandler(), "test", Locale.ENGLISH);
        
    }
	@Test
    public void testOutOfBounds5() throws Exception {
        
        String html1 = "<html><head></head><body><p>test</p><p>test</p></body></html>";
        String html2 = "<html><head></head><body></body></html>";
    
        DaisyDiff.diffHTML(new InputSource(new StringReader(html1)), new InputSource(new StringReader(html2)), new DefaultHandler(), "test", Locale.ENGLISH);
        
    }
	@Test
    public void testOutOfBounds6() throws Exception {
        
        String html1 = "<html><head></head><body></body></html>";
        String html2 = "<html><head></head><body><p>test</p><p>test</p></body></html>";
    
        DaisyDiff.diffHTML(new InputSource(new StringReader(html1)), new InputSource(new StringReader(html2)), new DefaultHandler(), "test", Locale.ENGLISH);
        
    }
    
}
