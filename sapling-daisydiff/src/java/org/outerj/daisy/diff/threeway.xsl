<?xml version="1.0"?>
<!--
  Copyright 2004 Guy Van den Broeck

  Licensed under the Apache License, Version 2.0 (the "License");
  you may not use this file except in compliance with the License.
  You may obtain a copy of the License at

      http://www.apache.org/licenses/LICENSE-2.0

  Unless required by applicable law or agreed to in writing, software
  distributed under the License is distributed on an "AS IS" BASIS,
  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
  See the License for the specific language governing permissions and
  limitations under the License.
-->
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform" version="1.0">
<xsl:output method="xml" indent="yes" encoding="UTF-8"/>

<xsl:template match="/">
   <merge>
   	  <xsl:choose>
   	  	<xsl:when test="//span[contains(@class,'diff-html-conflict')]">
      		<conflict>true</conflict>
      	</xsl:when>
      	<xsl:otherwise>
      		<conflict>false</conflict>
      	</xsl:otherwise>
      </xsl:choose>
      <body>
	     <xsl:apply-templates select="diffreport/diff/node()"/>
	  </body>
   </merge>
</xsl:template>

<xsl:template match="@*|node()">
  <xsl:choose>
    <xsl:when test="descendant::span[@class='diff-html-conflict-yours'] and not(preceding::span[1][@class='diff-html-conflict-yours']) and not(descendant::span[@class='diff-html-conflict-theirs'])">
        <xsl:call-template name="insertmessage">
          <xsl:with-param name="side">Your</xsl:with-param>
        </xsl:call-template>
    </xsl:when>
    <xsl:when test="descendant::span[@class='diff-html-conflict-theirs'] and not(preceding::span[1][@class='diff-html-conflict-theirs']) and not(descendant::span[@class='diff-html-conflict-yours'])">
        <xsl:call-template name="insertmessage">
          <xsl:with-param name="side">Other</xsl:with-param>
        </xsl:call-template>
    </xsl:when>
    <xsl:otherwise>
      <xsl:copy>
        <xsl:apply-templates select="@*|node()"/>
      </xsl:copy>
    </xsl:otherwise>
  </xsl:choose>
</xsl:template>

<xsl:template name="insertmessage">
  <xsl:param name="side"/>
  <xsl:choose>
    <xsl:when test="ancestor::table and not(name()='td')">
      <xsl:copy>
        <xsl:apply-templates select="@*|node()"/>
      </xsl:copy>
    </xsl:when>
    <xsl:when test="self::td or self::span[@class='image_caption']">
      <xsl:copy>
        <xsl:apply-templates select="@*" mode="nomessage"/>
        <strong class="editConflict">Edit conflict! <xsl:value-of select="$side"/> version:</strong>
        <xsl:apply-templates select="node()" mode="nomessage"/>
      </xsl:copy>
    </xsl:when>
    <xsl:otherwise>
      <strong class="editConflict">Edit conflict! <xsl:value-of select="$side"/> version:</strong>
      <xsl:copy>
        <xsl:apply-templates select="@*|node()" mode="nomessage"/>
      </xsl:copy>
    </xsl:otherwise>
  </xsl:choose>
  
</xsl:template>


<xsl:template match="@*|node()" mode="nomessage">
<xsl:copy>
  <xsl:apply-templates select="@*|node()" mode="nomessage"/>
</xsl:copy>
</xsl:template>

<xsl:template match="img" mode="nomessage">
<img>
  <xsl:copy-of select="@*"/>
</img>
</xsl:template>

<xsl:template match="img">
<img>
  <xsl:copy-of select="@*"/>
</img>
</xsl:template>

<xsl:template match="span[@class='diff-html-changed']">
  <xsl:apply-templates select="node()"/>
</xsl:template>

<xsl:template match="span[@class='diff-html-added']">
  <xsl:apply-templates select="node()"/>
</xsl:template>

<xsl:template match="span[@class='diff-html-removed']">
</xsl:template>

<xsl:template match="span[@class='diff-html-conflict-yours']|span[@class='diff-html-conflict-theirs']" mode="nomessage">
  <xsl:apply-templates select="node()" mode="nomessage"/>
</xsl:template>

<xsl:template match="span[@class='diff-html-conflict-yours']" >
  <strong>Edit conflict! Your version:</strong>
  <xsl:apply-templates select="node()"/>
</xsl:template>

<xsl:template match="span[@class='diff-html-conflict-theirs']" >
  <strong>Edit conflict! Other version:</strong>
  <xsl:apply-templates select="node()"/>
</xsl:template>

</xsl:stylesheet>
