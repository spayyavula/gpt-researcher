import { useEffect } from 'react';

declare global {
  interface Window {
    renderMathInElement?: (element: HTMLElement, options: object) => void;
  }
}

/**
 * Hook that triggers KaTeX auto-render on the document body
 * whenever the provided HTML content changes.
 * Requires KaTeX auto-render script to be loaded via CDN in layout.tsx.
 */
export function useKatexRender(htmlContent: string) {
  useEffect(() => {
    if (!htmlContent) return;

    // Small delay to ensure DOM is updated with new content
    const timer = setTimeout(() => {
      if (window.renderMathInElement) {
        const mathElements = document.querySelectorAll('.markdown-content');
        mathElements.forEach((el) => {
          window.renderMathInElement(el as HTMLElement, {
            delimiters: [
              { left: '\\[', right: '\\]', display: true },
              { left: '\\(', right: '\\)', display: false },
              { left: '$$', right: '$$', display: true },
              { left: '$', right: '$', display: false },
            ],
            throwOnError: false,
            trust: true,
          });
        });
      }
    }, 100);

    return () => clearTimeout(timer);
  }, [htmlContent]);
}
