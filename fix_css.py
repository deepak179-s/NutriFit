import re

with open('src/style.css', 'r') as f:
    css = f.read()

# Replace the first block (AI Coach Full Screen Mobile)
old_block1 = """  #content::after{content:"";display:block;min-height:calc(120px + env(safe-area-inset-bottom));flex-shrink:0}
  #content:has(#page-ai.active)::after{display:none}
  body:has(input:focus, select:focus) #sidebar{display:none}
  
  /* AI Coach Full Screen Mobile */
  body:has(#page-ai.active) #sidebar{display:none}
  body:has(#page-ai.active) #topbar{display:none}
  body:has(#page-ai.active) #mobile-ai-fab{display:none}
  #page-ai.active{padding-bottom:env(safe-area-inset-bottom);padding-top:env(safe-area-inset-top)}
  body:has(#page-ai.active) #content{padding:0}
  
  .mobile-back-btn{display:inline-flex!important}"""

new_block1 = """  #content::after{content:"";display:block;min-height:calc(120px + env(safe-area-inset-bottom));flex-shrink:0}
  body:has(input:focus, select:focus) #sidebar{display:none}
  
  /* AI Coach Full Screen Mobile */
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
  }
  
  .mobile-back-btn{display:inline-flex!important}"""

css = css.replace(old_block1, new_block1)

# Replace the second block
old_block2 = """  #page-ai{margin:0;overflow:hidden}
  .ai-layout{border:0;border-radius:0;box-shadow:none;background:var(--bg1)}
  .chat-main{padding:0 16px}
  .chat-header{padding:2px 2px 12px;background:var(--bg1)}
  .chat-history{padding:12px 2px 18px}
  .chat-msg{max-width:88%;font-size:15px;line-height:1.55}
  .chat-input-area{margin:0 0 2px 0;padding:6px 7px 6px 8px;border-radius:20px;background:var(--bg3);width:auto;align-self:stretch}
  .chat-input{font-size:16px;flex:1;min-width:0;}
  .chat-send-btn{width:42px;height:42px;flex-basis:42px;flex-shrink:0;}"""

new_block2 = """  .ai-layout{border:0;border-radius:0;box-shadow:none;background:transparent}
  .chat-main{padding:0}
  .chat-header{padding:12px 16px;background:var(--bg1);border-bottom:1px solid var(--border)}
  .chat-history{padding:16px 12px 24px}
  .chat-msg{max-width:88%;font-size:15px;line-height:1.55}
  .chat-input-area{margin:0;padding:10px 12px;border-radius:0;border:none;border-top:1px solid var(--border);background:var(--bg1);width:100%;box-sizing:border-box}
  .chat-input{font-size:16px;flex:1;min-width:0;background:var(--bg3);padding:10px 16px;border-radius:20px;height:42px}
  .chat-send-btn{width:42px;height:42px;flex-basis:42px;flex-shrink:0;}"""

css = css.replace(old_block2, new_block2)

with open('src/style.css', 'w') as f:
    f.write(css)

print("Replaced blocks successfully.")
