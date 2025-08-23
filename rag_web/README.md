# PharmaRAG - Pharmaceutical Corpora Library

A modern web application for browsing and viewing pharmaceutical documents organized in a searchable library format.

## Features

- **Corpora Library**: Browse pharmaceutical documents organized alphabetically by first letter
- **Search Functionality**: Search across all documents with real-time filtering
- **Document Viewer**: View markdown documents with proper formatting and readability
- **Responsive Design**: Modern UI built with Next.js and Tailwind CSS
- **Dark/Light Theme**: Toggle between light and dark themes

## Architecture

The application has been transformed from a chat-based RAG system to a document library system:

- **Left Panel**: Corpora Library with alphabetical grouping and search
- **Center Panel**: Document Viewer for displaying selected pharmaceutical documents
- **Removed**: Chat functionality, conversation management, and context panels

## Components

- `CorporaLibrary`: Left sidebar displaying documents organized alphabetically
- `DocumentViewer`: Center panel for rendering selected markdown documents
- `Header`: Application header with title and theme toggle
- `useCorpora`: Hook managing document data and selection state

## Getting Started

1. Install dependencies:
   ```bash
   npm install
   ```

2. Run the development server:
   ```bash
   npm run dev
   ```

3. Open [http://localhost:3000](http://localhost:3000) in your browser

## Document Structure

Documents are pharmaceutical information files in Markdown format, containing:
- Medicine names and descriptions
- Dosage information
- Pricing details
- Usage instructions
- Side effects and contraindications

## Search and Navigation

- Use the search bar to find specific medicines
- Click on any document to view its full content
- Documents are automatically grouped by the first letter of their name
- Search results ignore alphabetical grouping for easier discovery

## Technology Stack

- **Frontend**: Next.js 14 with TypeScript
- **Styling**: Tailwind CSS with custom theme system
- **State Management**: React hooks for local state
- **Build Tool**: Next.js build system
