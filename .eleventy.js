const { EleventyI18nPlugin } = require("@11ty/eleventy");
const inclusiveLangPlugin = require("@11ty/eleventy-plugin-inclusive-language");
const yaml = require("js-yaml");
const { DateTime } = require("luxon");

module.exports = function(eleventyConfig) {
    eleventyConfig.addPlugin(EleventyI18nPlugin, {
      defaultLanguage: "en",
      errorMode: "never"
    });
    eleventyConfig.addPlugin(inclusiveLangPlugin);
    eleventyConfig.addPassthroughCopy("assets");
    // Serve notebook files (HTML previews live under assets/notebooks/html,
    // but we also expose the raw .ipynb files for direct download)
    eleventyConfig.addPassthroughCopy({ "notebooks": "notebooks" });
    eleventyConfig.addDataExtension("yaml", (contents) => yaml.load(contents));
    // Copy Static Files to /_Site
    eleventyConfig.addPassthroughCopy({
      "./admin/config.yml": "./admin/config.yml",
    });

    // Date filter used in archive section
    eleventyConfig.addFilter("readableDate", (dateStr) => {
      return DateTime.fromISO(dateStr).toLocaleString(DateTime.DATE_FULL);
    });

    // Exclude spec and script files from template processing
    eleventyConfig.ignores.add("spec.md");
    eleventyConfig.ignores.add("scripts/**");
    // Exclude exported notebook HTML from template processing
    // (these files contain {{ }} syntax from notebook code cells)
    eleventyConfig.ignores.add("assets/notebooks/**");
  };