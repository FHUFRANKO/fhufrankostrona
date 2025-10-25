import React, { useState, useMemo } from 'react';
import ReactQuill from 'react-quill';
import 'react-quill/dist/quill.snow.css';
import EmojiPicker from 'emoji-picker-react';
import { Button } from './ui/button';
import { Smile } from 'lucide-react';

export const RichTextEditor = ({ value, onChange, placeholder }) => {
  const [showEmojiPicker, setShowEmojiPicker] = useState(false);
  const quillRef = React.useRef(null);

  // Custom toolbar configuration
  const modules = useMemo(() => ({
    toolbar: {
      container: [
        ['bold', 'italic'], // Pogrubienie i kursywa
        [{ 'color': ['#000000', '#FF0000', '#0000FF', '#008000'] }], // Kolory: czarny, czerwony, niebieski, zielony
        ['clean'] // Usuń formatowanie
      ],
    }
  }), []);

  const formats = [
    'bold', 'italic', 'color'
  ];

  const handleEmojiClick = (emojiObject) => {
    const quill = quillRef.current?.getEditor();
    if (quill) {
      const cursorPosition = quill.getSelection()?.index || 0;
      quill.insertText(cursorPosition, emojiObject.emoji);
      quill.setSelection(cursorPosition + emojiObject.emoji.length);
    }
    setShowEmojiPicker(false);
  };

  return (
    <div className="relative">
      <div className="mb-2 flex items-center gap-2">
        <span className="text-sm text-gray-600">Narzędzia formatowania:</span>
        <Button
          type="button"
          variant="outline"
          size="sm"
          onClick={() => setShowEmojiPicker(!showEmojiPicker)}
          className="flex items-center gap-2"
        >
          <Smile className="h-4 w-4" />
          Emotki
        </Button>
      </div>

      {showEmojiPicker && (
        <div className="absolute z-50 mb-2">
          <EmojiPicker
            onEmojiClick={handleEmojiClick}
            width={350}
            height={400}
            searchPlaceholder="Szukaj emotki..."
            previewConfig={{ showPreview: false }}
          />
        </div>
      )}

      <ReactQuill
        ref={quillRef}
        theme="snow"
        value={value}
        onChange={onChange}
        modules={modules}
        formats={formats}
        placeholder={placeholder || "Wpisz opis..."}
        style={{
          backgroundColor: 'white',
          borderRadius: '0.375rem',
          minHeight: '200px'
        }}
      />

      <style jsx global>{`
        .ql-toolbar {
          border-top-left-radius: 0.375rem;
          border-top-right-radius: 0.375rem;
          background-color: #f9fafb;
          border: 1px solid #e5e7eb;
        }
        .ql-container {
          border-bottom-left-radius: 0.375rem;
          border-bottom-right-radius: 0.375rem;
          border: 1px solid #e5e7eb;
          border-top: none;
          font-size: 14px;
          min-height: 200px;
        }
        .ql-editor {
          min-height: 200px;
        }
        .ql-editor.ql-blank::before {
          color: #9ca3af;
          font-style: normal;
        }
      `}</style>
    </div>
  );
};
