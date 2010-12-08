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
package org.outerj.daisy.diff.html;

import static org.junit.Assert.assertTrue;

import org.junit.Test;


/**
 * Unit tests for handling long lines of HTML.
 * 
 * @author kapelonk
 *
 */
public class LongHtmlTest {

	/**
	 * Issue 20 Reported by Peter Dibble
	 *  
	 * @throws Exception something went wrong.
	 */
	@Test
	public void longHtml1() throws Exception
	{
		String oldText = "<html> <body> <A HREF=\"../../javax/realtime/AsyncEventHandler.html#AsyncEventHandler(javax.realtime.SchedulingParameter, b)\">AsyncEventHandler</A> </body> </html>";
		String newText = "<html> <body> <A HREF=\"../../javax/realtime/BsyncEventHandler.html#AsyncEventHandler(javax.realtime.SchedulingParameter, b)\">AsyncEventHandler</A> </body> </html>";
		
		String result = HtmlTestFixture.diff(oldText, newText);
		assertTrue("Expected a change",result.indexOf("diff-html-changed") > -1);
	}
	
	
}
