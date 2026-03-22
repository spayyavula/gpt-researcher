import { remark } from 'remark';
import html from 'remark-html';
import remarkGfm from 'remark-gfm';
import remarkMath from 'remark-math';
import { Compatible } from "vfile";

/**
 * Adds target="_blank" and rel="noopener noreferrer" attributes to all links in HTML content
 * @param htmlContent - The HTML content containing links
 * @returns The processed HTML with target="_blank" added to all links
 */
export const addTargetBlankToLinks = (htmlContent: string): string => {
  return htmlContent.replace(
    /<a(.*?)href="(.*?)"(.*?)>/gi,
    '<a$1href="$2"$3 target="_blank" rel="noopener noreferrer">'
  );
};

/**
 * Fixes the list item paragraph issue in HTML content
 * This specifically addresses the problem where numbered list items with bold text
 * have an extra line break between the marker and content
 * @param htmlContent - The HTML content with possible list formatting issues
 * @returns The processed HTML with fixed list formatting
 */
export const fixListItemParagraphIssue = (htmlContent: string): string => {
  // This regex looks for list items with a paragraph immediately inside
  // and removes the paragraph tags while preserving the content
  return htmlContent.replace(
    /<li>\s*<p>([\s\S]*?)<\/p>/g,
    '<li>$1'
  );
};

/**
 * Renders LaTeX math expressions in HTML content using KaTeX.
 * Handles both display math ($$...$$) and inline math ($...$).
 * @param htmlContent - The HTML content potentially containing LaTeX expressions
 * @returns The processed HTML with rendered math expressions
 */
export const renderLatexExpressions = (htmlContent: string): string => {
  // Process display math first ($$...$$) - these become centered block equations
  htmlContent = htmlContent.replace(
    /\$\$([\s\S]*?)\$\$/g,
    (_, tex) => {
      const cleaned = tex.replace(/<[^>]*>/g, '').replace(/&amp;/g, '&').replace(/&lt;/g, '<').replace(/&gt;/g, '>').trim();
      return `<div class="math-display">\\[${cleaned}\\]</div>`;
    }
  );

  // Process inline math ($...$) - avoid matching $$
  htmlContent = htmlContent.replace(
    /(?<!\$)\$(?!\$)((?:[^$\\]|\\.)+?)\$(?!\$)/g,
    (_, tex) => {
      const cleaned = tex.replace(/<[^>]*>/g, '').replace(/&amp;/g, '&').replace(/&lt;/g, '<').replace(/&gt;/g, '>').trim();
      return `<span class="math-inline">\\(${cleaned}\\)</span>`;
    }
  );

  return htmlContent;
};

/**
 * Converts markdown to HTML with GitHub Flavored Markdown support, LaTeX math rendering,
 * and adds target="_blank" to links
 * @param markdown - The markdown content to convert
 * @returns Promise with the HTML content
 */
export const markdownToHtml = async (markdown: Compatible | string): Promise<string> => {
  try {
    const result = await remark()
      .use(remarkGfm) // Add GitHub Flavored Markdown support (tables, strikethrough, etc.)
      .use(remarkMath) // Parse math expressions ($...$ and $$...$$)
      .use(html, { sanitize: false })
      .process(markdown);

    // Get the HTML string
    let htmlString = result.toString();

    // Apply fixes
    htmlString = fixListItemParagraphIssue(htmlString);
    htmlString = addTargetBlankToLinks(htmlString);
    htmlString = renderLatexExpressions(htmlString);

    return htmlString;
  } catch (error) {
    console.error('Error converting Markdown to HTML:', error);
    return ''; // Handle error gracefully, return empty string or default content
  }
};
