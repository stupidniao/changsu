import { defineConfig, type UserConfigExport } from "@tarojs/cli";
import path from "node:path";

export default defineConfig(async (merge) => {
  const base: UserConfigExport = {
    projectName: "changsu",
    date: "2026-07-02",
    designWidth: 750,
    deviceRatio: {
      640: 2.34 / 2,
      750: 1,
      375: 2,
      828: 1.81 / 2,
    },
    sourceRoot: "src",
    outputRoot: "dist",
    plugins: [],
    defineConstants: {},
    copy: {
      patterns: [],
      options: {},
    },
    framework: "react",
    compiler: "webpack5",
    mini: {
      compile: {
        include: [path.resolve(__dirname, "../../../packages/shared")],
      },
      postcss: {
        pxtransform: {
          enable: true,
          config: {},
        },
        url: {
          enable: true,
          config: {
            limit: 1024,
          },
        },
        cssModules: {
          enable: false,
        },
      },
    },
    h5: {
      publicPath: "/",
      staticDirectory: "static",
      postcss: {
        autoprefixer: {
          enable: true,
        },
        cssModules: {
          enable: false,
        },
      },
    },
  };

  return merge({}, base);
});
