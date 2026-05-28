// main.js — SecureVault Password Manager
// Handles: password strength, show/hide toggle, clipboard copy,
//          password generator, sidebar toggle, delete confirmation

// 1. PASSWORD SHOW / HIDE TOGGLE


/**
 * Toggles a password input between visible text and hidden dots.
 * Updates the eye icon to match the current state.
 * @param {string} inputId - The ID of the password input element
 */
function togglePassword(inputId) {
  const input = document.getElementById(inputId);
  const icon  = document.getElementById('eyeIcon_' + inputId);

  if (!input) return;

  if (input.type === 'password') {
    input.type = 'text';
    if (icon) {
      icon.classList.remove('bi-eye');
      icon.classList.add('bi-eye-slash');
    }
  } else {
    input.type = 'password';
    if (icon) {
      icon.classList.remove('bi-eye-slash');
      icon.classList.add('bi-eye');
    }
  }
}


// 2. VAULT TABLE — Show/Hide individual password rows

/**
 * Toggles the password visibility for a specific vault row.
 * Switches between bullet dots and the actual plain-text password.
 * @param {number} id - Credential ID (used to find DOM elements)
 */
function toggleVaultPassword(id) {
  const dots  = document.getElementById('pwd-' + id);
  const plain = document.getElementById('pwdPlain-' + id);
  const eye   = document.getElementById('eyeVault-' + id);

  if (!dots || !plain) return;

  const isHidden = dots.classList.contains('hidden');

  if (isHidden) {
    // Currently showing plain → switch back to dots
    dots.classList.remove('hidden');
    plain.classList.add('hidden');
    eye.classList.remove('bi-eye-slash');
    eye.classList.add('bi-eye');
  } else {
    // Currently showing dots → show plain
    dots.classList.add('hidden');
    plain.classList.remove('hidden');
    eye.classList.remove('bi-eye');
    eye.classList.add('bi-eye-slash');
  }
}


// 3. CLIPBOARD COPY

/**
 * Copies a vault row's password to the clipboard.
 * Reads the already-decrypted plain text stored in the hidden span.
 * Shows a brief "Copied!" popup notification.
 * @param {number} id - Credential ID
 */
function copyPassword(id) {
  const plain = document.getElementById('pwdPlain-' + id);
  if (!plain) return;

  const password = plain.textContent;
  copyToClipboard(password);

  // Visual feedback on the copy icon
  const icon = document.getElementById('copyIcon-' + id);
  if (icon) {
    icon.classList.remove('bi-clipboard');
    icon.classList.add('bi-clipboard-check-fill');
    setTimeout(() => {
      icon.classList.remove('bi-clipboard-check-fill');
      icon.classList.add('bi-clipboard');
    }, 2000);
  }
}

/**
 * Copies any plain text value to clipboard.
 * Used for copying usernames inline.
 * @param {string} text     - Text to copy
 * @param {Element} btnEl   - The button element (for visual feedback)
 */
function copyText(text, btnEl) {
  copyToClipboard(text);
  if (btnEl) {
    const icon = btnEl.querySelector('i');
    if (icon) {
      icon.classList.remove('bi-clipboard');
      icon.classList.add('bi-clipboard-check-fill');
      btnEl.style.color = 'var(--neon-green)';
      setTimeout(() => {
        icon.classList.remove('bi-clipboard-check-fill');
        icon.classList.add('bi-clipboard');
        btnEl.style.color = '';
      }, 2000);
    }
  }
}

/**
 * Core clipboard copy function.
 * Uses the modern Clipboard API with fallback for older browsers.
 * Shows the green "Copied!" popup bubble at the bottom.
 * @param {string} text - Text to copy to clipboard
 */
function copyToClipboard(text) {
  if (navigator.clipboard && window.isSecureContext) {
    navigator.clipboard.writeText(text).then(() => showCopyPopup());
  } else {
    // Fallback for non-HTTPS environments
    const el = document.createElement('textarea');
    el.value = text;
    el.style.position = 'fixed';
    el.style.opacity = '0';
    document.body.appendChild(el);
    el.select();
    document.execCommand('copy');
    document.body.removeChild(el);
    showCopyPopup();
  }
}

/**
 * Shows the "Copied to clipboard!" floating popup briefly.
 */
function showCopyPopup() {
  const popup = document.getElementById('copyPopup');
  if (!popup) return;
  popup.classList.add('visible');
  setTimeout(() => popup.classList.remove('visible'), 2000);
}

// 4. PASSWORD STRENGTH METER

/**
 * Analyzes a password and updates the strength bar + label.
 * Scoring criteria:
 *   - Length >= 8     → +1 point
 *   - Length >= 12    → +1 point
 *   - Has uppercase   → +1 point
 *   - Has lowercase   → +1 point
 *   - Has number      → +1 point
 *   - Has symbol      → +1 point
 *
 * Score 0-1: Weak | 2-3: Fair | 4-5: Good | 6: Strong
 *
 * @param {string} password - The current value of the password field
 */
function checkPasswordStrength(password) {
  const bar    = document.getElementById('strengthFill');
  const label  = document.getElementById('strengthLabel');
  const meter  = bar ? bar.parentElement.parentElement : null;

  if (!bar || !label) return;

  // Clear all strength classes
  if (meter) {
    meter.classList.remove('strength-weak','strength-fair','strength-good','strength-strong');
  }

  if (!password || password.length === 0) {
    bar.style.width = '0%';
    bar.style.background = '';
    label.textContent = 'Enter a password';
    label.style.color = '';
    return;
  }

  // Score the password
  let score = 0;
  if (password.length >= 8)  score++;
  if (password.length >= 12) score++;
  if (/[A-Z]/.test(password)) score++;
  if (/[a-z]/.test(password)) score++;
  if (/[0-9]/.test(password)) score++;
  if (/[^A-Za-z0-9]/.test(password)) score++;

  // Map score to level
  let level, text, color;
  if (score <= 1) {
    level = 'strength-weak';   text = 'Weak';   color = 'var(--neon-red)';
  } else if (score <= 3) {
    level = 'strength-fair';   text = 'Fair';   color = 'var(--neon-yellow)';
  } else if (score <= 4) {
    level = 'strength-good';   text = 'Good';   color = '#00ccff';
  } else {
    level = 'strength-strong'; text = 'Strong'; color = 'var(--neon-green)';
  }

  if (meter) meter.classList.add(level);
  label.textContent = text;
  label.style.color = color;
}
// 5. PASSWORD MATCH CHECKER (Setup Form)

/**
 * Checks if the confirm password field matches the master password field.
 * Updates the match status text below the confirm field in real-time.
 */
function checkMatch() {
  const pass    = document.getElementById('masterPasswordInput');
  const confirm = document.getElementById('confirmPasswordInput');
  const status  = document.getElementById('matchStatus');

  if (!pass || !confirm || !status) return;

  if (confirm.value.length === 0) {
    status.textContent = '';
    return;
  }

  if (pass.value === confirm.value) {
    status.textContent = '✓ Passwords match';
    status.className   = 'match-status match-ok';
  } else {
    status.textContent = '✗ Passwords do not match';
    status.className   = 'match-status match-fail';
  }
}

// 6. PASSWORD GENERATOR

/**
 * Generates a random password based on selected options.
 * Places the generated password into the specified input field.
 * Triggers strength meter update after generation.
 * @param {string} targetInputId - ID of the input to fill (default: 'newPasswordInput')
 */
function generatePassword(targetInputId = 'newPasswordInput') {
  const length    = parseInt(document.getElementById('genLength')?.value)  || 16;
  const useUpper  = document.getElementById('genUpper')?.checked  ?? true;
  const useNums   = document.getElementById('genNumbers')?.checked ?? true;
  const useSyms   = document.getElementById('genSymbols')?.checked ?? true;

  const lower   = 'abcdefghijklmnopqrstuvwxyz';
  const upper   = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ';
  const numbers = '0123456789';
  const symbols = '!@#$%^&*()_+-=[]{}|;:,.<>?';

  // Build character pool
  let pool = lower;
  if (useUpper) pool += upper;
  if (useNums)  pool += numbers;
  if (useSyms)  pool += symbols;

  // Generate password from pool
  let password = '';
  for (let i = 0; i < length; i++) {
    const randomIndex = Math.floor(Math.random() * pool.length);
    password += pool[randomIndex];
  }

  // Fill in the target input field
  const input = document.getElementById(targetInputId);
  if (input) {
    input.value = password;
    input.type  = 'text'; // Show it as plain text after generating

    // Update the eye icon
    const eye = document.getElementById('eyeIcon_' + targetInputId);
    if (eye) {
      eye.classList.remove('bi-eye');
      eye.classList.add('bi-eye-slash');
    }

    // Trigger strength meter update
    checkPasswordStrength(password);
  }
}

// 7. DELETE CONFIRMATION DIALOG

/**
 * Shows a confirmation dialog before deleting a credential.
 * Returns true (proceed) or false (cancel).
 * @param {string} siteName - Optional website name to display in dialog
 * @returns {boolean}
 */
function confirmDelete(siteName = '') {
  const msg = siteName
    ? `Are you sure you want to delete the credential for "${siteName}"?\n\nThis action cannot be undone.`
    : 'Are you sure you want to delete this credential?\n\nThis action cannot be undone.';
  return window.confirm(msg);
}
// 8. SIDEBAR TOGGLE (Mobile)

/**
 * Toggles the sidebar open/closed on mobile screens.
 * Adds/removes the 'open' class which slides it in via CSS.
 */
function toggleSidebar() {
  const sidebar = document.getElementById('sidebar');
  if (sidebar) {
    sidebar.classList.toggle('open');
  }
}

// Close sidebar when clicking outside it on mobile
document.addEventListener('click', function(e) {
  const sidebar = document.getElementById('sidebar');
  const toggle  = document.getElementById('menuToggle');

  if (!sidebar) return;

  // If click is outside sidebar and not on the toggle button
  if (!sidebar.contains(e.target) && e.target !== toggle && !toggle?.contains(e.target)) {
    if (window.innerWidth <= 768) {
      sidebar.classList.remove('open');
    }
  }
});
// 9. AUTO-DISMISS TOASTS

// Toasts auto-dismiss after 4 seconds (also handled inline in base.html)
document.addEventListener('DOMContentLoaded', function () {
  setTimeout(() => {
    document.querySelectorAll('.toast').forEach(t => {
      t.style.transition = 'opacity 0.4s ease';
      t.style.opacity    = '0';
      setTimeout(() => t.remove(), 400);
    });
  }, 4000);
});
