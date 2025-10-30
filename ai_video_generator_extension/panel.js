(function() {
  const panel = document.getElementById('sidePanel');
  const closeBtn = document.getElementById('closeBtn');
  const fullscreenBtn = document.getElementById('fullscreenBtn');
  const iframe = document.getElementById('panelIframe');

  // Close panel
  if (closeBtn) {
    closeBtn.addEventListener('click', () => {
      if (panel) {
        panel.style.animation = 'slideOut 0.3s ease-out';
        setTimeout(() => {
          panel.remove();
        }, 300);
      }
    });
  }

  // Toggle fullscreen
  if (fullscreenBtn) {
    fullscreenBtn.addEventListener('click', () => {
      if (panel) {
        panel.classList.toggle('fullscreen');
      }
    });
  }

  console.log('AI Video Side Panel loaded successfully!');
})();

// Add slideOut animation
const style = document.createElement('style');
style.textContent = `
  @keyframes slideOut {
    from {
      transform: translateX(0);
      opacity: 1;
    }
    to {
      transform: translateX(100%);
      opacity: 0;
    }
  }
`;
// document.head.appendChild(style);
