declare module 'codemirror/addon/lint/lint.js' {
  import CodeMirror from 'codemirror';

  export interface ILintingEditor extends CodeMirror.Editor {}
}
