import React, { createContext, useContext, useEffect, useState } from "react";
import {
  SupportedLanguage,
  DEFAULT_LANGUAGE,
  LANGUAGE_STORAGE_KEY,
  LANGUAGES,
} from "./languages";
import { en } from "./en";
import { hi } from "./hi";

type TranslationDictionary = Record<string, Record<string, string>>;

interface LanguageContextType {
  language: SupportedLanguage;
  setLanguage: (lang: SupportedLanguage) => void;
  t: (path: string, params?: Record<string, string | number>) => string;
  isHindi: boolean;
}

const dictionaries: Record<SupportedLanguage, TranslationDictionary> = {
  en,
  hi,
};

const KNOWN_FALLBACKS: Record<string, string> = {
  "quizzes.assigned": "Assigned Quizzes",
  "quiz.title": "Assigned Quizzes",
  "skillGaps.intelligenceTitle": "Skill Gap Intelligence",
  "skillGaps.intelligenceSubtitle": "Deficits between your verified capability levels and statutory role requirements.",
  "skillGaps.roleRequirements": "Role Requirements",
};

function formatFallbackKey(path: string): string {
  if (KNOWN_FALLBACKS[path]) {
    return KNOWN_FALLBACKS[path];
  }

  const parts = path.split(".");
  const leaf = parts[parts.length - 1] || path;

  let text = leaf;
  if ((leaf === "title" || leaf === "subtitle" || leaf === "assigned") && parts.length > 1) {
    const parent = parts[parts.length - 2];
    text = `${parent} ${leaf}`;
  }

  const words = text
    .replace(/([a-z])([A-Z])/g, "$1 $2")
    .replace(/[_-]+/g, " ")
    .trim()
    .split(/\s+/)
    .map((w) => w.charAt(0).toUpperCase() + w.slice(1).toLowerCase());

  return words.join(" ") || path;
}

export const LanguageContext = createContext<LanguageContextType>({
  language: DEFAULT_LANGUAGE,
  setLanguage: () => {},
  t: (path: string) => formatFallbackKey(path),
  isHindi: false,
});

export const LanguageProvider: React.FC<{ children: React.ReactNode }> = ({
  children,
}) => {
  const [language, setLanguageState] = useState<SupportedLanguage>(() => {
    const saved = localStorage.getItem(LANGUAGE_STORAGE_KEY) as SupportedLanguage;
    if (saved && (saved === "en" || saved === "hi")) {
      return saved;
    }
    return DEFAULT_LANGUAGE;
  });

  const setLanguage = (lang: SupportedLanguage) => {
    setLanguageState(lang);
    localStorage.setItem(LANGUAGE_STORAGE_KEY, lang);
    document.documentElement.lang = lang;
  };

  useEffect(() => {
    document.documentElement.lang = language;
  }, [language]);

  const t = (path: string, params?: Record<string, string | number>): string => {
    const keys = path.split(".");
    let current: any = dictionaries[language] || dictionaries.en;

    for (const key of keys) {
      if (current && typeof current === "object" && key in current) {
        current = current[key];
      } else {
        // Fallback to English dictionary if key missing in current language
        let fallback: any = dictionaries.en;
        let foundFallback = true;
        for (const fbKey of keys) {
          if (fallback && typeof fallback === "object" && fbKey in fallback) {
            fallback = fallback[fbKey];
          } else {
            foundFallback = false;
            break;
          }
        }
        current = foundFallback ? fallback : undefined;
        break;
      }
    }

    let result: string;
    if (typeof current === "string") {
      result = current;
    } else {
      result = formatFallbackKey(path);
    }

    if (params) {
      for (const [pKey, pVal] of Object.entries(params)) {
        result = result.replace(new RegExp(`{${pKey}}`, "g"), String(pVal));
      }
    }

    return result;
  };

  return (
    <LanguageContext.Provider
      value={{
        language,
        setLanguage,
        t,
        isHindi: language === "hi",
      }}
    >
      {children}
    </LanguageContext.Provider>
  );
};
