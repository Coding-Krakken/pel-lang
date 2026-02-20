#!/bin/bash
# My Personal PEL Workflow
# Quick commands I use to analyze my consulting business

echo "🚀 Consulting Business Analysis Workflow"
echo "=========================================="
echo ""

# Step 1: Validate the model
echo "📋 Step 1: Checking model for errors..."
./pel check my_consulting_business.pel
if [ $? -ne 0 ]; then
    echo "❌ Model has errors! Fix them first."
    exit 1
fi
echo "✅ Model is valid!"
echo ""

# Step 2: Compile
echo "⚙️  Step 2: Compiling model..."
./pel compile my_consulting_business.pel -o my_consulting.ir.json
if [ $? -ne 0 ]; then
    echo "❌ Compilation failed!"
    exit 1
fi
echo "✅ Compilation successful!"
echo ""

# Step 3: Run deterministic projection
echo "📊 Step 3: Running 12-month projection..."
./pel run my_consulting.ir.json \
    --mode deterministic \
    --seed 42 \
    --horizon 12 \
    -o my_consulting_results.json
if [ $? -ne 0 ]; then
    echo "❌ Execution failed!"
    exit 1
fi
echo "✅ Projection complete!"
echo ""

# Step 4: View results
echo "📈 Step 4: Displaying results..."
echo ""
python3 beginner_examples/view_results.py my_consulting_results.json
echo ""

# Optional: Show raw JSON for deeper analysis
echo "💡 Tip: View raw data with:"
echo "   cat my_consulting_results.json | jq '.variables.revenue'"
echo ""
echo "📄 Full report available at: BUSINESS_REPORT.md"
echo ""
echo "✅ Analysis complete!"
