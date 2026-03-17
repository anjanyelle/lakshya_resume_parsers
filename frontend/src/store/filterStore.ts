import { create } from "zustand";

type FilterState = {
  searchTerm: string;
  skills: string[];
  location: string;
  minExperience: number | null;
  maxExperience: number | null;
  setSearchTerm: (value: string) => void;
  setSkills: (skills: string[]) => void;
  setLocation: (value: string) => void;
  setExperience: (min: number | null, max: number | null) => void;
  resetFilters: () => void;
};

export const useFilterStore = create<FilterState>((set) => ({
  searchTerm: "",
  skills: [],
  location: "",
  minExperience: null,
  maxExperience: null,
  setSearchTerm: (searchTerm) => set({ searchTerm }),
  setSkills: (skills) => set({ skills }),
  setLocation: (location) => set({ location }),
  setExperience: (minExperience, maxExperience) =>
    set({ minExperience, maxExperience }),
  resetFilters: () =>
    set({
      searchTerm: "",
      skills: [],
      location: "",
      minExperience: null,
      maxExperience: null,
    }),
}));
