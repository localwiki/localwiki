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

import java.util.ArrayList;
import java.util.List;

import org.outerj.daisy.diff.output.TextDiffOutput;

/**
 * Minimal test case for Tag mode.
 * 
 * @author kapelonk
 *
 */
public class TagTestFixture {
	
	/** Type of changes as produced by the diff process */
	private enum OperationType {
		NO_CHANGE, ADD_TEXT, REMOVE_TEXT
	}

	/** Keeps a copy of the original text */
	private String oldText = null;
	
	/** Keeps a copy of the modified text */
	private String newText = null;
	
	/** A list of text operations produced by the diff process */
	private List<TextOperation> results = null;
	

	/**
	 * Just empties the results;
	 */
	public TagTestFixture()
	{
		results = new ArrayList<TextOperation>();
	}
	
	/**
	 * Performs a tag diff againts two html strings.
	 * 
	 * @param original html in its old state.
	 * @param modified html in its present state.
	 * 
	 * @throws Exception something went wrong.
	 */
	public void performTagDiff(String original, String modified) throws Exception
	{
		oldText = original;
		newText = modified;
		
		TagComparator oldComp = new TagComparator(oldText);
		TagComparator newComp = new TagComparator(newText);
        
        DummyOutput output = new DummyOutput();
        TagDiffer differ = new TagDiffer(output);
        differ.diff(oldComp, newComp);
        
	}
	
	/**
	 * Attempts to re-construct the original text by looking 
	 * at the diff result.
	 * 
	 * @return the sum of unchanged and removed text.
	 */
	public String getReconstructedOriginalText()
	{
		StringBuilder result = new StringBuilder();
		
		for(TextOperation operation:results)
		{
			if(operation.getType() == OperationType.ADD_TEXT)
			{
				continue;
			}
			result.append(operation.getText());
		}
		return result.toString();
	}
	
	/**
	 * Attempts to re-construct the modified text by looking 
	 * at the diff result.
	 * 
	 * @return the sum of unchanged and added text.
	 */
	public String getReconstructedModifiedText()
	{
		StringBuilder result = new StringBuilder();
		
		for(TextOperation operation:results)
		{
			if(operation.getType() == OperationType.REMOVE_TEXT)
			{
				continue;
			}
			result.append(operation.getText());
		}
		return result.toString();
	}
	
	/**
	 * Retuns a list of basic operations.
	 * @return the results
	 */
	public List<TextOperation> getResults() {
		return results;
	}



    /**
     * Simple operation for test cases only.
     * 
     * @author kapelonk
     *
     */
	private static class TextOperation
	{
		private String text = null;
		private OperationType type = null;
		
		/**
		 * @param text the text to set
		 */
		public void setText(String text) {
			this.text = text;
		}

		/**
		 * @param type the type to set
		 */
		public void setType(OperationType type) {
			this.type = type;
		}

		/**
		 * @return the text
		 */
		public String getText() {
			return text;
		}
		
		/**
		 * @return the type
		 */
		public OperationType getType() {
			return type;
		}
		
	}
	
	/** 
	 * Dummy output that holds all results in a linear list.
	 * 
	 * @author kapelonk
	 *
	 */
	private class DummyOutput implements TextDiffOutput
	{

		/**
		 * {@inheritDoc}
		 */
		public void addAddedPart(String text) throws Exception {
			TextOperation operation = new TextOperation();
			operation.setText(text);
			operation.setType(OperationType.ADD_TEXT);
			results.add(operation);
			
		}

		/**
		 * {@inheritDoc}
		 */
		public void addClearPart(String text) throws Exception {
			TextOperation operation = new TextOperation();
			operation.setText(text);
			operation.setType(OperationType.NO_CHANGE);
			results.add(operation);
			
		}

		/**
		 * {@inheritDoc}
		 */
		public void addRemovedPart(String text) throws Exception {
			TextOperation operation = new TextOperation();
			operation.setText(text);
			operation.setType(OperationType.REMOVE_TEXT);
			results.add(operation);
			
		}
		
	}

	
}
