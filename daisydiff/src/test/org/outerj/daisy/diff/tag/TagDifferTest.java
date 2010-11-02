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
package org.outerj.daisy.diff.tag;

import static org.junit.Assert.assertEquals;

import org.junit.Test;

/**
 * Simple examples for Tag diffing.
 * 
 * @author kapelonk
 * 
 */
public class TagDifferTest {

	/**
	 * Adding a single word. 
	 * @throws Exception something went wrong.
	 */
	@Test
	public void simpleTextAdd() throws Exception {
		String oldText = "<p> This is a blue book</p>";
		String newText = "<p> This is a big blue book</p>";

		TagTestFixture tagTest = new TagTestFixture();
		tagTest.performTagDiff(oldText, newText);
		assertEquals("Expected 3 operations", 3, tagTest.getResults().size());
		assertEquals("Expected original text", oldText, tagTest
				.getReconstructedOriginalText());
		assertEquals("Expected modified text", newText, tagTest
				.getReconstructedModifiedText());

	}

	/**
	 * Removing a single word.
	 * @throws Exception something went wrong.
	 */
	@Test
	public void simpleTextRemove() throws Exception {
		String oldText = "<p> This is a blue book</p>";
		String newText = "<p> This is a book</p>";

		TagTestFixture tagTest = new TagTestFixture();
		tagTest.performTagDiff(oldText, newText);
		assertEquals("Expected 3 operations", 3, tagTest.getResults().size());
		assertEquals("Expected original text", oldText, tagTest
				.getReconstructedOriginalText());
		assertEquals("Expected modified text", newText, tagTest
				.getReconstructedModifiedText());
	}

	/**
	 * Changing a single word. 
	 * @throws Exception something went wrong.
	 */
	@Test
	public void simpleTextChange() throws Exception {
		String oldText = "<p> This is a blue book</p>";
		String newText = "<p> This is a green book</p>";

		TagTestFixture tagTest = new TagTestFixture();
		tagTest.performTagDiff(oldText, newText);
		assertEquals("Expected 4 operations", 4, tagTest.getResults().size());
		assertEquals("Expected original text", oldText, tagTest
				.getReconstructedOriginalText());
		assertEquals("Expected modified text", newText, tagTest
				.getReconstructedModifiedText());
	}

	/**
	 * Adding an HTML attribute.
	 * 
	 * @throws Exception something went wrong.
	 */
	@Test
	public void simpleAttributeAdd() throws Exception {
		String oldText = "<p> This is a blue book</p>";
		String newText = "<p id='sample'> This is a blue book</p>";

		TagTestFixture tagTest = new TagTestFixture();
		tagTest.performTagDiff(oldText, newText);
		assertEquals("Expected 4 operations", 4, tagTest.getResults().size());
		assertEquals("Expected original text", oldText, tagTest
				.getReconstructedOriginalText());
		assertEquals("Expected modified text", newText, tagTest
				.getReconstructedModifiedText());
	}

	/**
	 * Adding an HTML tag.
	 * 
	 * @throws Exception something went wrong.
	 */
	@Test
	public void simpleTagAdd() throws Exception {
		String oldText = "<p> This is a blue book</p>";
		String newText = "<p> This is a <b>blue</b> book</p>";

		TagTestFixture tagTest = new TagTestFixture();
		tagTest.performTagDiff(oldText, newText);
		assertEquals("Expected 5 operations", 5, tagTest.getResults().size());
		assertEquals("Expected original text", oldText, tagTest
				.getReconstructedOriginalText());
		assertEquals("Expected modified text", newText, tagTest
				.getReconstructedModifiedText());
	}

	/**
	 * Two text changes.
	 * 
	 * @throws Exception something went wrong.
	 */
	@Test
	public void twiceChangeText() throws Exception {
		String oldText = "<p> This is a blue book</p>";
		String newText = "<p> This is a red table</p>";

		TagTestFixture tagTest = new TagTestFixture();
		tagTest.performTagDiff(oldText, newText);
		assertEquals("Expected 4 operations", 4, tagTest.getResults().size());
		assertEquals("Expected original text", oldText, tagTest
				.getReconstructedOriginalText());
		assertEquals("Expected modified text", newText, tagTest
				.getReconstructedModifiedText());
	}

}
