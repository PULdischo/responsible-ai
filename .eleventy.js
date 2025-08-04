const { EleventyI18nPlugin } = require("@11ty/eleventy");
const inclusiveLangPlugin = require("@11ty/eleventy-plugin-inclusive-language");
const yaml = require("js-yaml");

module.exports = function(eleventyConfig) {
    eleventyConfig.addPlugin(EleventyI18nPlugin, {
      // any valid BCP 47-compatible language tag is supported
      defaultLanguage: "en", // Required, this site uses "en"
      errorMode: "never"
    });
    eleventyConfig.addPlugin(inclusiveLangPlugin);
    eleventyConfig.addPassthroughCopy("assets");
    eleventyConfig.addDataExtension("yaml", (contents) => yaml.load(contents));
    // Copy Static Files to /_Site
    eleventyConfig.addPassthroughCopy({
    "./admin/config.yml": "./admin/config.yml",
    });
    
  };