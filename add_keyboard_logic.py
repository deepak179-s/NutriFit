import re

with open('src/app.js', 'r') as f:
    js = f.read()

# Replace the visualViewport logic I added previously
old_code = """// Handle mobile keyboard open/close
if (window.visualViewport) {
  window.visualViewport.addEventListener('resize', () => {
    const historyEl = document.getElementById('chat-history');
    if (historyEl) historyEl.scrollTop = historyEl.scrollHeight;
  });
} else {
  window.addEventListener('resize', () => {
    const historyEl = document.getElementById('chat-history');
    if (historyEl) historyEl.scrollTop = historyEl.scrollHeight;
  });
}"""

new_code = """// Handle mobile keyboard open/close and bottom spacing
function handleResize() {
  const historyEl = document.getElementById('chat-history');
  if (historyEl) historyEl.scrollTop = historyEl.scrollHeight;
  
  // Detect keyboard open on mobile
  if (window.innerWidth <= 720) {
    const viewportHeight = window.visualViewport ? window.visualViewport.height : window.innerHeight;
    const isKeyboardOpen = viewportHeight < window.screen.availHeight * 0.8;
    if (isKeyboardOpen) {
      document.body.classList.add('keyboard-open');
    } else {
      document.body.classList.remove('keyboard-open');
    }
  } else {
    document.body.classList.remove('keyboard-open');
  }
}

if (window.visualViewport) {
  window.visualViewport.addEventListener('resize', handleResize);
}
window.addEventListener('resize', handleResize);
// Run once on load
setTimeout(handleResize, 100);"""

if old_code in js:
    js = js.replace(old_code, new_code)
else:
    # Just append it
    js += "\n\n" + new_code

with open('src/app.js', 'w') as f:
    f.write(js)

print("Updated app.js")
