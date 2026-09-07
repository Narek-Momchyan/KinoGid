export interface LogoData {
    url?: string;
    alt?: string;
}

export interface NavbarCategory {
    id: number;
    href: string;
    name: string;
    slug: string;
    lang: string;
    navbar: number;
}

export interface NavbarItem {
    id: number;
    title: string;
    slug: string;
    lang: string;
    href?: string;
    order?: number;
    categories?: NavbarCategory[];
}

export interface LanguageItem {
    code: string;
    name?: string;
}

export interface HeaderData {
    logo?: LogoData;
    navbar?: NavbarItem[];
    languages?: LanguageItem[];
}
