(function() {
  'use strict';

  var TRAVEL_EMOJIS = ['🚌', '✈️', '🏨', '🍽️', '📸', '🌄', '⛰️', '🌊', '⛺', '🎒', '🕒', '📍', '✨', '🌿', '🚗', '⛵', '🧭', '🔥'];

  var quillToolbarOptions = [
    [{ 'header': [1, 2, 3, 4, false] }],
    [{ 'size': ['small', false, 'large', 'huge'] }],
    ['bold', 'italic', 'underline', 'strike'],
    [{ 'color': [] }, { 'background': [] }],
    [{ 'list': 'ordered'}, { 'list': 'bullet' }],
    [{ 'align': [] }],
    ['link', 'image'],
    ['clean']
  ];

  function initQuillOnTextarea(textarea) {
    if (!textarea || textarea.dataset.quillInitialized === 'true') {
      return;
    }

    // Mark as initialized
    textarea.dataset.quillInitialized = 'true';
    textarea.style.display = 'none';

    // Create container wrapper
    var wrapper = document.createElement('div');
    wrapper.className = 'quill-editor-wrapper';

    // Create emoji toolbar
    var emojiBar = document.createElement('div');
    emojiBar.className = 'quill-emoji-bar';
    var emojiLabel = document.createElement('span');
    emojiLabel.className = 'quill-emoji-bar-label';
    emojiLabel.textContent = 'Travel Emojis:';
    emojiBar.appendChild(emojiLabel);

    // Create Quill container
    var editorDiv = document.createElement('div');
    
    wrapper.appendChild(editorDiv);
    wrapper.appendChild(emojiBar);
    textarea.parentNode.insertBefore(wrapper, textarea.nextSibling);

    // Initialize Quill instance
    var quill = new Quill(editorDiv, {
      theme: 'snow',
      placeholder: 'Enter day-by-day plan or itinerary overview...',
      modules: {
        toolbar: quillToolbarOptions
      }
    });

    // Populate initial content
    if (textarea.value) {
      quill.root.innerHTML = textarea.value;
    }

    // Attach emojis click handlers
    TRAVEL_EMOJIS.forEach(function(emoji) {
      var btn = document.createElement('button');
      btn.type = 'button';
      btn.className = 'quill-emoji-btn';
      btn.textContent = emoji;
      btn.title = 'Insert ' + emoji;
      btn.addEventListener('click', function(e) {
        e.preventDefault();
        var range = quill.getSelection(true);
        quill.insertText(range.index, emoji + ' ');
        quill.setSelection(range.index + emoji.length + 1);
        textarea.value = quill.root.innerHTML;
      });
      emojiBar.appendChild(btn);
    });

    // Real-time sync to textarea
    quill.on('text-change', function() {
      textarea.value = quill.root.innerHTML;
    });

    // Sync on form submit
    var form = textarea.closest('form');
    if (form) {
      form.addEventListener('submit', function() {
        textarea.value = quill.root.innerHTML;
      });
    }
  }

  function initAllQuillEditors() {
    if (typeof Quill === 'undefined') {
      return;
    }
    var textareas = document.querySelectorAll('.quill-wysiwyg-editor');
    textareas.forEach(function(ta) {
      // Don't initialize template textareas inside Django inline empty form
      if (ta.name && ta.name.indexOf('__prefix__') === -1) {
        initQuillOnTextarea(ta);
      }
    });
  }

  // Initial load
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initAllQuillEditors);
  } else {
    initAllQuillEditors();
  }

  // Handle Django inline dynamic row additions
  document.addEventListener('formset:added', function(event) {
    if (event.detail && event.detail.formsetName) {
      setTimeout(initAllQuillEditors, 50);
    }
  });

  // Fallback observer if Quill script loads slightly later
  window.addEventListener('load', function() {
    initAllQuillEditors();
  });
})();
