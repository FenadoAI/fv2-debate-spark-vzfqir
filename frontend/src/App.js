import { useState } from "react";
import "./App.css";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import axios from "axios";
import { Button } from "./components/ui/button";
import { Input } from "./components/ui/input";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "./components/ui/card";

const API_BASE = process.env.REACT_APP_API_URL || 'https://8001-irinajr69yng4kycuc4o4.e2b.app';
const API = `${API_BASE}/api`;

const Home = () => {
  const [topic, setTopic] = useState("");
  const [debateData, setDebateData] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState("");

  const generateDebateArguments = async () => {
    if (!topic.trim()) {
      setError("Please enter a debate topic");
      return;
    }

    setIsLoading(true);
    setError("");

    try {
      const response = await axios.post(`${API}/generate-debate`, {
        topic: topic.trim()
      });

      setDebateData(response.data);
    } catch (err) {
      console.error("Error generating debate arguments:", err);
      setError("Failed to generate debate arguments. Please try again.");
    } finally {
      setIsLoading(false);
    }
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    generateDebateArguments();
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 p-4">
      <div className="max-w-6xl mx-auto">
        {/* Header */}
        <div className="text-center mb-12 pt-8">
          <h1 className="text-4xl font-bold text-gray-800 mb-4">
            Debate Prep Generator
          </h1>
          <p className="text-xl text-gray-600 max-w-2xl mx-auto">
            Get balanced, well-researched arguments for both sides of any debate topic
          </p>
        </div>

        {/* Input Section */}
        <Card className="mb-8 shadow-lg">
          <CardHeader>
            <CardTitle className="text-2xl">Enter Your Debate Topic</CardTitle>
            <CardDescription>
              Type any topic you want to debate about, and we'll generate key arguments for both sides
            </CardDescription>
          </CardHeader>
          <CardContent>
            <form onSubmit={handleSubmit} className="space-y-4">
              <div className="flex gap-4">
                <Input
                  type="text"
                  placeholder="e.g., Should social media be regulated by government?"
                  value={topic}
                  onChange={(e) => setTopic(e.target.value)}
                  className="flex-1 text-lg h-12"
                  disabled={isLoading}
                />
                <Button
                  type="submit"
                  disabled={isLoading || !topic.trim()}
                  className="px-8 h-12 text-lg"
                >
                  {isLoading ? "Generating..." : "Generate"}
                </Button>
              </div>
              {error && (
                <p className="text-red-600 text-sm">{error}</p>
              )}
            </form>
          </CardContent>
        </Card>

        {/* Results Section */}
        {debateData && (
          <div className="grid md:grid-cols-2 gap-6 mb-8">
            {/* Arguments For */}
            <Card className="shadow-lg border-green-200">
              <CardHeader className="bg-green-50">
                <CardTitle className="text-2xl text-green-800 flex items-center gap-2">
                  <span className="text-3xl">✓</span>
                  Arguments FOR
                </CardTitle>
                <CardDescription className="text-green-700">
                  {debateData.topic}
                </CardDescription>
              </CardHeader>
              <CardContent className="pt-6">
                <div className="space-y-6">
                  {debateData.arguments_for.map((argument, index) => (
                    <div key={index} className="border-l-4 border-green-500 pl-4">
                      <h4 className="font-semibold text-gray-800 mb-2">
                        {index + 1}. {argument.point}
                      </h4>
                      <ul className="space-y-1">
                        {argument.supporting_facts.map((fact, factIndex) => (
                          <li key={factIndex} className="text-gray-600 text-sm flex items-start gap-2">
                            <span className="text-green-500 font-bold">•</span>
                            {fact}
                          </li>
                        ))}
                      </ul>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>

            {/* Arguments Against */}
            <Card className="shadow-lg border-red-200">
              <CardHeader className="bg-red-50">
                <CardTitle className="text-2xl text-red-800 flex items-center gap-2">
                  <span className="text-3xl">✗</span>
                  Arguments AGAINST
                </CardTitle>
                <CardDescription className="text-red-700">
                  {debateData.topic}
                </CardDescription>
              </CardHeader>
              <CardContent className="pt-6">
                <div className="space-y-6">
                  {debateData.arguments_against.map((argument, index) => (
                    <div key={index} className="border-l-4 border-red-500 pl-4">
                      <h4 className="font-semibold text-gray-800 mb-2">
                        {index + 1}. {argument.point}
                      </h4>
                      <ul className="space-y-1">
                        {argument.supporting_facts.map((fact, factIndex) => (
                          <li key={factIndex} className="text-gray-600 text-sm flex items-start gap-2">
                            <span className="text-red-500 font-bold">•</span>
                            {fact}
                          </li>
                        ))}
                      </ul>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          </div>
        )}

        {/* Sample Topics */}
        {!debateData && (
          <Card className="shadow-lg">
            <CardHeader>
              <CardTitle className="text-xl">Sample Topics to Try</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid md:grid-cols-2 gap-3">
                {[
                  "Should social media be regulated by government?",
                  "Is remote work better than office work?",
                  "Should college education be free?",
                  "Is artificial intelligence a threat to jobs?",
                  "Should animal testing be banned?",
                  "Is nuclear energy a viable solution for climate change?"
                ].map((sampleTopic, index) => (
                  <Button
                    key={index}
                    variant="outline"
                    onClick={() => setTopic(sampleTopic)}
                    className="text-left h-auto p-3 justify-start"
                    disabled={isLoading}
                  >
                    {sampleTopic}
                  </Button>
                ))}
              </div>
            </CardContent>
          </Card>
        )}

        {/* Footer */}
        <div className="text-center mt-12 pb-8">
          <p className="text-gray-600">
            Powered by AI • Built for better debates
          </p>
        </div>
      </div>
    </div>
  );
};

function App() {
  return (
    <div className="App">
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<Home />}>
            <Route index element={<Home />} />
          </Route>
        </Routes>
      </BrowserRouter>
    </div>
  );
}

export default App;
