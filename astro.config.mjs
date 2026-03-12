// @ts-check

import mdx from '@astrojs/mdx';
import sitemap from '@astrojs/sitemap';
import { defineConfig } from 'astro/config';

import vitePwa from '@vite-pwa/astro';

import vercel from '@astrojs/vercel';
import remarkGfm from 'remark-gfm';

// https://astro.build/config
export default defineConfig({
    site: 'https://nm-statistics.vercel.app', // Placeholder
    base: '/',
    output: 'server',
    markdown: {
        remarkPlugins: [remarkGfm],
    },

    integrations: [
        mdx({
            remarkPlugins: [remarkGfm],
        }),
        sitemap(),
        {
            name: "disable-dev-toolbar",
            hooks: {
                "astro:config:setup": ({ updateConfig }) => {
                    updateConfig({
                        devToolbar: {
                            enabled: false
                        }
                    });
                }
            }
        },
        vitePwa({
            registerType: 'autoUpdate',
            manifest: {
                name: '핵의학 검사 통계',
                short_name: '핵의학통계',
                description: '핵의학 검사 통계 서비스',
                start_url: '/',
                theme_color: '#ffffff',
                background_color: '#ffffff',
                display: 'standalone',
                lang: 'ko',
                icons: [
                    {
                        src: '/icon-192.png',
                        sizes: '192x192',
                        type: 'image/png',
                    },
                    {
                        src: '/icon-512.png',
                        sizes: '512x512',
                        type: 'image/png',
                    },
                ],
            },
            workbox: {
                globPatterns: ['**/*.{js,css,html,ico,png,svg,webp,woff,woff2}'],
                navigateFallback: null,
                runtimeCaching: [
                    {
                        urlPattern: ({ request }) => request.mode === 'navigate',
                        handler: 'NetworkFirst',
                        options: {
                            cacheName: 'pages',
                            networkTimeoutSeconds: 5,
                        },
                    },
                ],
            },
            devOptions: {
                enabled: true,
            },
        }),
    ],

    adapter: vercel(),
});
