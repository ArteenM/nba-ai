import Header from '@/components/Header';

export default function AboutPage() {
  return (
    <div className="min-h-screen bg-gray-50">
      <Header />
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="max-w-4xl mx-auto">
          <h1 className="text-3xl font-bold text-gray-900 mb-8">About HoopPredict</h1>
          
          {/* How the model works */}
          <div className="bg-white rounded-lg shadow-md border border-gray-200 p-8 mb-8">
            <h2 className="text-2xl font-bold text-gray-900 mb-6">How the Model Works</h2>
            <div className="space-y-4">
              <div className="flex items-start">
                <div className="flex-shrink-0 w-6 h-6 bg-blue-100 rounded-full flex items-center justify-center mr-4 mt-1">
                  <span className="text-blue-600 font-semibold text-sm">1</span>
                </div>
                <div>
                  <h3 className="font-semibold text-gray-900 mb-2">Data Collection</h3>
                  <p className="text-gray-600">
                    Our AI model analyzes comprehensive NBA data including team statistics, player performance, 
                    historical matchups, injury reports, and situational factors like home/away records and rest days.
                  </p>
                </div>
              </div>
              
              <div className="flex items-start">
                <div className="flex-shrink-0 w-6 h-6 bg-blue-100 rounded-full flex items-center justify-center mr-4 mt-1">
                  <span className="text-blue-600 font-semibold text-sm">2</span>
                </div>
                <div>
                  <h3 className="font-semibold text-gray-900 mb-2">Machine Learning Processing</h3>
                  <p className="text-gray-600">
                    Advanced machine learning algorithms process this data to identify patterns and trends 
                    that influence game outcomes, using techniques like ensemble methods and deep learning.
                  </p>
                </div>
              </div>
              
              <div className="flex items-start">
                <div className="flex-shrink-0 w-6 h-6 bg-blue-100 rounded-full flex items-center justify-center mr-4 mt-1">
                  <span className="text-blue-600 font-semibold text-sm">3</span>
                </div>
                <div>
                  <h3 className="font-semibold text-gray-900 mb-2">Real-time Analysis</h3>
                  <p className="text-gray-600">
                    The model continuously updates its predictions as new data becomes available, 
                    incorporating live game statistics and in-game developments for maximum accuracy.
                  </p>
                </div>
              </div>
              
              <div className="flex items-start">
                <div className="flex-shrink-0 w-6 h-6 bg-blue-100 rounded-full flex items-center justify-center mr-4 mt-1">
                  <span className="text-blue-600 font-semibold text-sm">4</span>
                </div>
                <div>
                  <h3 className="font-semibold text-gray-900 mb-2">Prediction Generation</h3>
                  <p className="text-gray-600">
                    Based on the analysis, the model generates win probabilities, point spreads, 
                    and other key metrics to help users make informed decisions about NBA games.
                  </p>
                </div>
              </div>
            </div>
          </div>

          {/* About us */}
          <div className="bg-white rounded-lg shadow-md border border-gray-200 p-8">
            <h2 className="text-2xl font-bold text-gray-900 mb-6">About Us</h2>
            <div className="prose prose-gray max-w-none">
              <p className="text-gray-600 leading-relaxed mb-4">
                HoopPredict was born from a passion for basketball and cutting-edge technology. 
                Our team of data scientists, software engineers, and basketball enthusiasts came together 
                to create the most accurate NBA game prediction platform available.
              </p>
              <p className="text-gray-600 leading-relaxed mb-4">
                We believe that the future of sports analysis lies in the intersection of artificial intelligence 
                and human expertise. By combining advanced machine learning models with deep basketball knowledge, 
                we provide insights that help fans, analysts, and enthusiasts better understand the beautiful game.
              </p>
              <p className="text-gray-600 leading-relaxed">
                Our mission is to democratize access to professional-grade NBA analysis, making sophisticated 
                predictions and insights available to everyone who loves the game. Whether you&apos;re a casual fan 
                or a serious analyst, HoopPredict empowers you with the data and insights you need to stay ahead of the game.
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
