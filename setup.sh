#!/bin/bash

echo "🚀 Setting up External API Tester..."
echo ""

# Check if .env exists
if [ -f ".env" ]; then
    echo "⚠️  .env file already exists!"
    read -p "Do you want to overwrite it? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "❌ Setup cancelled. Keeping existing .env file."
        exit 1
    fi
fi

# Copy env.example to .env
echo "📝 Copying env.example to .env..."
cp env.example .env

if [ $? -eq 0 ]; then
    echo "✅ .env file created successfully!"
    echo ""
    echo "📋 OAuth2 credentials configured for all 6 environments:"
    echo "   - Capricorn API Trunk (Dev)"
    echo "   - Capricorn Rapid Production"
    echo "   - Capricorn Standard Production"
    echo "   - Capricorn Rapid Stage"
    echo "   - Capricorn Standard Stage"
    echo "   - External API Local"
    echo ""
    echo "🎯 Next steps:"
    echo "   1. (Optional) Edit .env if you need to update credentials"
    echo "   2. Start the application:"
    echo "      - Development: docker-compose -f docker-compose.dev.yml up --build"
    echo "      - Production:  docker-compose up --build"
    echo "   3. Open: http://localhost:5000/test-runner"
    echo ""
    echo "📖 For more information, see ENV_SETUP_GUIDE.md"
else
    echo "❌ Failed to create .env file"
    exit 1
fi

