import re

with open('src/style.css', 'r') as f:
    css = f.read()

# Replace the AI Coach Full Screen Mobile block
old_block1 = """  /* AI Coach Full Screen Mobile */
  #page-ai.active {
    position: fixed !important;
    inset: 0;
    height: 100dvh;
    z-index: 999;
    margin: 0 !important;
    padding: env(safe-area-inset-top) 0 env(safe-area-inset-bottom) 0 !important;
    background: var(--bg1);
    box-sizing: border-box;
  }
  body:has(#page-ai.active) #sidebar,
  body:has(#page-ai.active) #topbar,
  body:has(#page-ai.active) #mobile-ai-fab {
    display: none !important;
  }"""

new_block1 = """  /* AI Coach Full Screen Mobile */
  #page-ai.active {
    position: fixed !important;
    inset: 0;
    height: 100dvh;
    z-index: 90;
    margin: 0 !important;
    /* 72px sidebar + 10px spacing = 82px */
    padding: env(safe-area-inset-top) 0 calc(82px + env(safe-area-inset-bottom)) 0 !important;
    background: var(--bg1);
    box-sizing: border-box;
  }
  body.keyboard-open #page-ai.active {
    padding-bottom: env(safe-area-inset-bottom) !important;
  }
  body.keyboard-open #sidebar {
    display: none !important;
  }
  body:has(#page-ai.active) #topbar,
  body:has(#page-ai.active) #mobile-ai-fab {
    display: none !important;
  }"""

if old_block1 in css:
    css = css.replace(old_block1, new_block1)
    print("Replaced AI block.")
else:
    print("Could not find AI block.")

# Wait! The `:has(input:focus, select:focus)` might also be hiding the sidebar, which is good.
# Let's keep it but enhance it.

with open('src/style.css', 'w') as f:
    f.write(css)

