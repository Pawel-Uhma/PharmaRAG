// Medicine names data structure
export interface MedicineNamesData {
  names: string[];
  total_count: number;
}

export interface MedicineNamesMetadata {
  total_count: number;
  extracted_at: string;
  source: string;
  version: string;
}

export interface MedicineNamesFullData {
  metadata: MedicineNamesMetadata;
  names: string[];
}
