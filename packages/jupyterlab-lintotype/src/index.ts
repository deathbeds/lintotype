import { NotebookPanel } from '@jupyterlab/notebook';

import { Token } from '@phosphor/coreutils';

export const NAME = '@deathbeds/jupyterlab-lintotype';
export const VERSION = '0.1.0';
export const PLUGIN_ID = `${NAME}:ILintotypeManager`;

export interface ILintotypeManager {
  lintifyNotebook(panel: NotebookPanel): void;
}

export const ILintotypeManager = new Token<ILintotypeManager>(PLUGIN_ID);
