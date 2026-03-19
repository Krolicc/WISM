import { createApp } from 'vue'
import { createPinia } from 'pinia'

import App from './App.vue'
import { vTooltipHelper } from './directives/tooltip-helper';
import { actionHintDirective } from './directives/action-hint';

const app = createApp(App)

app.use(createPinia())

app.directive('tooltip-helper', vTooltipHelper);
app.directive('action-hint', actionHintDirective);

app.mount('#app')
