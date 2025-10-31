// Content script that injects the side panel
(function() {
  // Check if panel already exists
  if (document.getElementById('ai-video-side-panel')) {
    return;
  }

  // Create the panel container
  const panelContainer = document.createElement('div');
  panelContainer.id = 'ai-video-side-panel';
  
  // Load the panel HTML
  const panelUrl = chrome.runtime.getURL('panel.html');
  
  fetch(panelUrl)
    .then(response => response.text())
    .then(html => {
      panelContainer.innerHTML = html;
      document.body.appendChild(panelContainer);
      
      // Load and inject CSS
      const link = document.createElement('link');
      link.rel = 'stylesheet';
      link.href = chrome.runtime.getURL('panel.css');
      document.head.appendChild(link);
      
      // Load and execute panel JS
      const script = document.createElement('script');
      script.src = chrome.runtime.getURL('panel.js');
      document.body.appendChild(script);
    })
    .catch(error => console.error('Error loading panel:', error));
})();