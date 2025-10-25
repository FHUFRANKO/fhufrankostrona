import React, { useState, useRef } from 'react';
import EmojiPicker from 'emoji-picker-react';
import { Button } from './ui/button';
import { Smile, Bold, Italic, Type, Hash, List } from 'lucide-react';

export const RichTextEditor = ({ value, onChange, placeholder }) => {
  const [showEmojiPicker, setShowEmojiPicker] = useState(false);
  const [showColorPicker, setShowColorPicker] = useState(false);
  const textareaRef = useRef(null);

  const colors = [
    { name: 'Czarny', value: '#000000' },
    { name: 'Czerwony', value: '#FF0000' },
    { name: 'Niebieski', value: '#0000FF' },
    { name: 'Zielony', value: '#008000' },
  ];

  const insertTag = (openTag, closeTag) => {
    const textarea = textareaRef.current;
    if (!textarea) return;

    const start = textarea.selectionStart;
    const end = textarea.selectionEnd;
    const selectedText = value.substring(start, end);
    const newText = value.substring(0, start) + openTag + selectedText + closeTag + value.substring(end);
    
    onChange(newText);
    
    // Przywróć fokus i pozycję kursora
    setTimeout(() => {
      textarea.focus();
      const newPosition = start + openTag.length + selectedText.length + closeTag.length;
      textarea.setSelectionRange(newPosition, newPosition);
    }, 0);
  };

  const insertAtCursor = (text) => {
    const textarea = textareaRef.current;
    if (!textarea) return;

    const cursorPosition = textarea.selectionStart;
    const newText = value.substring(0, cursorPosition) + text + value.substring(cursorPosition);
    
    onChange(newText);
    
    setTimeout(() => {
      textarea.focus();
      const newPosition = cursorPosition + text.length;
      textarea.setSelectionRange(newPosition, newPosition);
    }, 0);
  };

  const handleBold = () => {
    insertTag('<strong>', '</strong>');
  };

  const handleItalic = () => {
    insertTag('<em>', '</em>');
  };

  const handleColor = (color) => {
    insertTag(`<span style="color: ${color}">`, '</span>');
    setShowColorPicker(false);
  };

  const handleHashtag = () => {
    const textarea = textareaRef.current;
    if (!textarea) return;

    const start = textarea.selectionStart;
    const end = textarea.selectionEnd;
    const selectedText = value.substring(start, end);
    
    // Jeśli jest zaznaczony tekst, dodaj # przed nim
    if (selectedText) {
      const newText = value.substring(0, start) + '# ' + selectedText + value.substring(end);
      onChange(newText);
      setTimeout(() => {
        textarea.focus();
        textarea.setSelectionRange(start + 2, end + 2);
      }, 0);
    } else {
      // Jeśli nie ma zaznaczenia, po prostu wstaw #
      insertAtCursor('# ');
    }
  };

  const handleNewLine = () => {
    insertAtCursor('\n');
  };

  const handleBulletList = () => {
    const textarea = textareaRef.current;
    if (!textarea) return;

    const start = textarea.selectionStart;
    const end = textarea.selectionEnd;
    const selectedText = value.substring(start, end);
    
    if (selectedText) {
      // Podziel na linie i dodaj myślnik do każdej
      const lines = selectedText.split('\n');
      const bulletedText = lines.map(line => line.trim() ? `- ${line.trim()}` : line).join('\n');
      const newText = value.substring(0, start) + bulletedText + value.substring(end);
      onChange(newText);
    } else {
      insertAtCursor('- ');
    }
  };

  const handleEmojiClick = (emojiObject) => {
    const textarea = textareaRef.current;
    if (!textarea) return;

    const cursorPosition = textarea.selectionStart;
    const newText = value.substring(0, cursorPosition) + emojiObject.emoji + value.substring(cursorPosition);
    
    onChange(newText);
    setShowEmojiPicker(false);
    
    setTimeout(() => {
      textarea.focus();
      const newPosition = cursorPosition + emojiObject.emoji.length;
      textarea.setSelectionRange(newPosition, newPosition);
    }, 0);
  };

  // Render HTML preview
  const renderPreview = () => {
    // Konwertuj zwykły tekst z formatowaniem na HTML
    let html = value;
    
    // Zachowaj nowe linie
    html = html.replace(/\n/g, '<br>');
    
    return { __html: html };
  };

  return (
    <div className="space-y-2">
      {/* Toolbar */}
      <div className="flex flex-wrap items-center gap-2 p-2 bg-gray-50 border border-gray-300 rounded-t-lg">
        <span className="text-sm text-gray-600 mr-2">Formatowanie:</span>
        
        <Button
          type="button"
          variant="outline"
          size="sm"
          onClick={handleBold}
          title="Pogrubienie (zaznacz tekst)"
          className="h-8 w-8 p-0"
        >
          <Bold className="h-4 w-4" />
        </Button>

        <Button
          type="button"
          variant="outline"
          size="sm"
          onClick={handleItalic}
          title="Kursywa (zaznacz tekst)"
          className="h-8 w-8 p-0"
        >
          <Italic className="h-4 w-4" />
        </Button>

        <div className="relative">
          <Button
            type="button"
            variant="outline"
            size="sm"
            onClick={() => setShowColorPicker(!showColorPicker)}
            title="Kolor tekstu (zaznacz tekst)"
            className="h-8 px-2 flex items-center gap-1"
          >
            <Type className="h-4 w-4" />
            <span className="text-xs">Kolor</span>
          </Button>

          {showColorPicker && (
            <div className="absolute top-full left-0 mt-1 bg-white border border-gray-300 rounded shadow-lg p-2 z-50">
              <div className="flex flex-col gap-1">
                {colors.map((color) => (
                  <button
                    key={color.value}
                    type="button"
                    onClick={() => handleColor(color.value)}
                    className="flex items-center gap-2 px-3 py-2 hover:bg-gray-100 rounded text-sm"
                  >
                    <div 
                      className="w-4 h-4 rounded border border-gray-300" 
                      style={{ backgroundColor: color.value }}
                    />
                    {color.name}
                  </button>
                ))}
              </div>
            </div>
          )}
        </div>

        <Button
          type="button"
          variant="outline"
          size="sm"
          onClick={handleHashtag}
          title="Hashtag #"
          className="h-8 px-2 flex items-center gap-1"
        >
          <Hash className="h-4 w-4" />
          <span className="text-xs">#</span>
        </Button>

        <Button
          type="button"
          variant="outline"
          size="sm"
          onClick={handleBulletList}
          title="Lista z myślnikami"
          className="h-8 px-2 flex items-center gap-1"
        >
          <List className="h-4 w-4" />
          <span className="text-xs">Lista</span>
        </Button>

        <div className="relative">
          <Button
            type="button"
            variant="outline"
            size="sm"
            onClick={() => setShowEmojiPicker(!showEmojiPicker)}
            title="Emotki"
            className="h-8 px-2 flex items-center gap-1"
          >
            <Smile className="h-4 w-4" />
            <span className="text-xs">Emotki</span>
          </Button>

          {showEmojiPicker && (
            <div className="absolute top-full left-0 mt-1 z-50">
              <EmojiPicker
                onEmojiClick={handleEmojiClick}
                width={320}
                height={400}
                searchPlaceholder="Szukaj emotki..."
                previewConfig={{ showPreview: false }}
              />
            </div>
          )}
        </div>
      </div>

      {/* Editor */}
      <textarea
        ref={textareaRef}
        value={value}
        onChange={(e) => onChange(e.target.value)}
        placeholder={placeholder || "Wpisz opis...\n\nWskazówki:\n- Użyj Enter aby dodać nową linię\n- Zaznacz tekst i kliknij 'B' aby pogrubić\n- Użyj # aby dodać hashtag\n- Kliknij 'Lista' aby dodać myślniki"}
        rows={12}
        className="w-full px-4 py-3 border border-gray-300 rounded-b-lg font-sans text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
        style={{ 
          minHeight: '300px',
          lineHeight: '1.6',
          whiteSpace: 'pre-wrap'
        }}
      />

      {/* Character count */}
      <p className="text-gray-500 text-sm">
        {value.replace(/<[^>]*>/g, '').length}/10000 znaków
      </p>

      {/* Preview */}
      <div className="mt-3 p-4 bg-gray-50 rounded border border-gray-200">
        <p className="text-xs font-semibold text-gray-600 mb-2">Podgląd opisu (jak będzie wyglądać na stronie):</p>
        <div 
          className="text-sm text-gray-800 whitespace-pre-line"
          style={{ lineHeight: '1.4' }}
          dangerouslySetInnerHTML={renderPreview()}
        />
      </div>
    </div>
  );
};
