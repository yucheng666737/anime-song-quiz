import { writeFileSync } from 'node:fs';

const config = {
  graphqlUrl: process.env.APP_GRAPHQL_URL || 'https://graphql.animethemes.moe/',
  apiBase: process.env.APP_API_BASE || '',
  mediaProxyUrl: process.env.APP_MEDIA_PROXY_URL || ''
};

const content = `// Auto-generated at build time. Do not commit.\nwindow.APP_CONFIG = ${JSON.stringify(config, null, 2)};\n`;
writeFileSync('config.js', content, 'utf8');
console.log('Generated config.js');
