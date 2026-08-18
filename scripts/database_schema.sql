-- Enable pgvector extension for similarity search
CREATE EXTENSION IF NOT EXISTS vector;

-- 1. Profiles Table (linking to auth.users)
CREATE TABLE profiles (
    id UUID PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
    full_name TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL
);

-- 2. Cases Table
CREATE TABLE cases (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES profiles(id) ON DELETE CASCADE,
    title TEXT NOT NULL,
    status TEXT DEFAULT 'open',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL
);

-- 3. Case Messages Table
CREATE TABLE case_messages (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    case_id UUID REFERENCES cases(id) ON DELETE CASCADE,
    role TEXT NOT NULL CHECK (role IN ('user', 'assistant', 'system')),
    content JSONB NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL
);

-- 4. Documents Table (Metadata for Supabase Storage)
CREATE TABLE documents (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    case_id UUID REFERENCES cases(id) ON DELETE CASCADE,
    user_id UUID REFERENCES profiles(id) ON DELETE CASCADE,
    storage_path TEXT NOT NULL,
    file_name TEXT NOT NULL,
    file_type TEXT NOT NULL,
    metadata JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL,
    processing_status TEXT DEFAULT 'pending'
);

-- 4b. Document Claims
CREATE TABLE document_claims (
    claim_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    document_id UUID REFERENCES documents(id) ON DELETE CASCADE,
    claim_type TEXT,
    field TEXT,
    value TEXT,
    page_number INTEGER,
    source_text TEXT,
    confidence TEXT DEFAULT 'High'
);

-- 5. Evidence Items
CREATE TABLE evidence_items (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    case_id UUID REFERENCES cases(id) ON DELETE CASCADE,
    type TEXT NOT NULL,
    description TEXT NOT NULL,
    is_provided BOOLEAN DEFAULT false,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL
);

-- 6. Action Plans
CREATE TABLE action_plans (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    case_id UUID REFERENCES cases(id) ON DELETE CASCADE,
    steps JSONB NOT NULL,
    generated_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL
);

-- 7. Legal Sources
CREATE TABLE legal_sources (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    title TEXT NOT NULL,
    type TEXT NOT NULL CHECK (type IN ('constitution', 'act', 'rule', 'regulation', 'judgment', 'government_procedure', 'legal_aid', 'official_guidance', 'form')),
    authority TEXT,
    jurisdiction JSONB,
    effective_date DATE,
    last_verified_at TIMESTAMP WITH TIME ZONE,
    source_version TEXT,
    status TEXT,
    is_active BOOLEAN DEFAULT true,
    source_url TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL
);

-- 8. Legal Chunks (with Vector Embeddings)
CREATE TABLE legal_chunks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    source_id UUID REFERENCES legal_sources(id) ON DELETE CASCADE,
    chunk_text TEXT NOT NULL,
    page_number INTEGER,
    section TEXT,
    embedding vector(768) NOT NULL, -- Assuming Gemini 2 embedding size (768)
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL
);

-- 9. Legal Aid Resources
CREATE TABLE legal_aid_resources (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name TEXT NOT NULL,
    jurisdiction JSONB,
    eligibility_criteria JSONB,
    url TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL
);

-- Setup basic RLS (Row Level Security)
ALTER TABLE profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE cases ENABLE ROW LEVEL SECURITY;
ALTER TABLE case_messages ENABLE ROW LEVEL SECURITY;
ALTER TABLE documents ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can view own profile" ON profiles FOR SELECT USING (auth.uid() = id);
CREATE POLICY "Users can update own profile" ON profiles FOR UPDATE USING (auth.uid() = id);

CREATE POLICY "Users can view their own cases" ON cases FOR SELECT USING (auth.uid() = user_id);
CREATE POLICY "Users can insert their own cases" ON cases FOR INSERT WITH CHECK (auth.uid() = user_id);
CREATE POLICY "Users can update their own cases" ON cases FOR UPDATE USING (auth.uid() = user_id);

CREATE POLICY "Users can view messages for own cases" ON case_messages FOR SELECT USING (
  case_id IN (SELECT id FROM cases WHERE user_id = auth.uid())
);
CREATE POLICY "Users can view own documents" ON documents FOR SELECT USING (auth.uid() = user_id);

-- Phase 5: Retrieval RPC
CREATE OR REPLACE FUNCTION match_legal_chunks(
  query_embedding vector(768),
  match_threshold float,
  match_count int,
  jurisdiction_filter jsonb,
  active_only boolean
)
RETURNS TABLE (
  id uuid,
  source_id uuid,
  title text,
  authority text,
  jurisdiction jsonb,
  type text,
  chunk_text text,
  section text,
  similarity float
)
LANGUAGE plpgsql
AS $$
BEGIN
  RETURN QUERY
  SELECT
    c.id,
    c.source_id,
    s.title,
    s.authority,
    s.jurisdiction,
    s.type,
    c.chunk_text,
    c.section,
    1 - (c.embedding <=> query_embedding) AS similarity
  FROM legal_chunks c
  JOIN legal_sources s ON c.source_id = s.id
  WHERE 1 - (c.embedding <=> query_embedding) > match_threshold
    AND (active_only = false OR s.is_active = true)
    -- Include specific matches or centrally applicable laws (empty jurisdiction {})
    AND (jurisdiction_filter = '{}'::jsonb OR s.jurisdiction @> jurisdiction_filter OR s.jurisdiction = '{}'::jsonb)
  ORDER BY c.embedding <=> query_embedding
  LIMIT match_count;
END;
$$;
