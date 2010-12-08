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
 * Simple examples for HTML diffing.
 * 
 * @author kapelonk
 *
 */
public class HTMLDifferTest {

	/**
	 * Adding a single word. 
	 * @throws Exception something went wrong.
	 */
	@Test
	public void simpleTextAdd() throws Exception
	{
		String oldText = "<p> This is a blue book</p>";
		String newText = "<p> This is a big blue book</p>";
		
		String result = HtmlTestFixture.diff(oldText, newText);
		assertTrue("Expected an addition",result.indexOf("<p> This is a <span class=\"diff-html-added\"") > -1);
	}
	
	/**
	 * Removing a single word.
	 * @throws Exception something went wrong.
	 */
	@Test 
	public void simpleTextRemove() throws Exception
	{
		String oldText = "<p> This is a blue book</p>";
		String newText = "<p> This is a book</p>";
		
		String result = HtmlTestFixture.diff(oldText, newText);
		assertTrue("Expected an removal",result.indexOf("<p> This is a <span class=\"diff-html-removed\"") > -1);
	}
	
	/**
	 * Changing a single word. 
	 * @throws Exception something went wrong.
	 */
	@Test 
	public void simpleTextChange() throws Exception
	{
		String oldText = "<p> This is a blue book</p>";
		String newText = "<p> This is a green book</p>";
		
		String result = HtmlTestFixture.diff(oldText, newText);
		assertTrue("Expected an removal",result.indexOf("<p> This is a <span class=\"diff-html-removed\"") > -1);
		assertTrue("Expected an addition",result.indexOf("blue </span><span class=\"diff-html-added\"") > -1);
	}
	
	/**
	 * Adding an HTML attribute.
	 * 
	 * @throws Exception something went wrong.
	 */
	@Test 
	public void simpleAttributeAdd() throws Exception
	{
		String oldText = "<p> This is a blue book</p>";
		String newText = "<p id='sample'> This is a blue book</p>";
		
		String result = HtmlTestFixture.diff(oldText, newText);
		assertTrue("Expected a change",result.indexOf("<p id=\"sample\"><span class=\"diff-html-changed\"") > -1);
	}
	

	/**
	 * Adding an HTML tag.
	 * 
	 * @throws Exception something went wrong.
	 */
	@Test 
	public void simpleTagAdd() throws Exception
	{
		String oldText = "<p> This is a blue book</p>";
		String newText = "<p> This is a <b>blue</b> book</p>";
		
		String result = HtmlTestFixture.diff(oldText, newText);
		assertTrue("Expected a change",result.indexOf("<p> This is a <b><span class=\"diff-html-changed\"") > -1);
	}
	
	/**
	 * Two text changes.
	 * 
	 * @throws Exception something went wrong.
	 */
	@Test 
	public void twiceChangeText() throws Exception
	{
		String oldText = "<p> This is a blue book</p>";
		String newText = "<p> This is a red table</p>";
		
		String result = HtmlTestFixture.diff(oldText, newText);
		assertTrue("Expected a removal",result.indexOf("<p> This is a <span class=\"diff-html-removed\"") > -1);
		assertTrue("Expected an addition",result.indexOf("<span class=\"diff-html-added\"") > -1);
	}
}
