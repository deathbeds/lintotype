import { Application, IPlugin } from '@phosphor/application';
import { Widget } from '@phosphor/widgets';


import { NAME, VERSION } from '.';

import * as CodeMirror from 'codemirror';

import '../style/index.css';

const EXTENSION_ID = `${NAME}:plugin`;

const plugin: IPlugin<Application<Widget>, void> = {
  id: EXTENSION_ID,
  requires: [],
  autoStart: true,
  activate: (app: Application<Widget>) => {
    console.log('lintotype', app, CodeMirror);
  }
};

export default plugin;
