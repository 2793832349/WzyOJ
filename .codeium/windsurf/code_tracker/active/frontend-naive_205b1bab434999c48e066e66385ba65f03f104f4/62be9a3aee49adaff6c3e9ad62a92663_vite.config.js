¦
import { defineConfig } from 'vite';
import AutoImport from 'unplugin-auto-import/vite';
import Components from 'unplugin-vue-components/vite';
import vue from '@vitejs/plugin-vue';
import { resolve } from 'path';
import { NaiveUiResolver } from 'unplugin-vue-components/resolvers';

export default defineConfig({
  resolve: {
    alias: {
      '@': resolve(__dirname, 'src'),
    },
  },
  plugins: [
    vue(),
    AutoImport({
      imports: [
        'vue',
        {
          'naive-ui': [
            'useDialog',
            'useMessage',
            'useNotification',
            'useLoadingBar',
          ],
        },
      ],
    }),
    Components({
      resolvers: [NaiveUiResolver()],
    }),
  ],
  build: {
    rollupOptions: {
      output: {
        // Force new hash by including timestamp in chunk names
        chunkFileNames: `assets/[name].[hash].${Date.now()}.js`,
        entryFileNames: `assets/[name].[hash].${Date.now()}.js`,
        assetFileNames: `assets/[name].[hash].[ext]`,
      },
    },
  },
  server: {
    proxy: {
      '/api': {
        target: 'http://127.0.0.1:8000',
        changeOrigin: true,
        rewrite: path => path.replace(/^\/api/, ''),
      },
      '/admin': {
        target: 'http://127.0.0.1:8000',
        changeOrigin: true,
      },
    },
  },
});
¦
*cascade08"(205b1bab434999c48e066e66385ba65f03f104f42*file:///root/frontend-naive/vite.config.js:file:///root/frontend-naive