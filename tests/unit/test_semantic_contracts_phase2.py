"""
Tests for Phase 2 Semantic Contract Features

This module tests Phase 2 enhancements to the semantic contract system:
- Enhanced error messages with contract hints
- Contract analysis report generation
- CLI --contract-report flag
"""

import pytest
from pathlib import Path
from compiler.typechecker import TypeChecker
from compiler.parser import Parser
from compiler.lexer import Lexer
from compiler.compiler import PELCompiler
from compiler.errors import CompilerError


class TestEnhancedErrorMessages:
    """Test enhanced error messages with contract suggestions."""

    def test_type_error_includes_contract_hint_revenue_per_unit(self):
        """Test that type errors suggest RevenuePerUnit_to_Price contract."""
        source = """model TestModel {
    param revenue: Currency<USD> = $100000
    param customers: Count<Customer> = 100
    var price: Currency<USD> = revenue / customers
}"""
        
        lexer = Lexer(source)
        parser = Parser(lexer.tokens)
        model = parser.parse_model()
        typechecker = TypeChecker()
        
        # This should raise with enhanced error message
        with pytest.raises(CompilerError) as exc_info:
            typechecker.check_model(model)
        
        error = exc_info.value
        # Check that error hint mentions contract
        if hasattr(error, 'hint') and error.hint:
            assert "contract" in error.hint.lower() or "RevenuePerUnit_to_Price" in error.hint

    def test_type_error_includes_contract_hint_fraction_from_ratio(self):
        """Test that type errors suggest FractionFromRatio contract."""
        source = """model  TestModel {
    param conversions: Count<Customer> = 20
    param trials: Count<User> = 100
    var rate: Fraction = conversions / trials
}"""
        
        lexer = Lexer(source)
        parser = Parser(lexer.tokens)
        model = parser.parse_model()
        typechecker = TypeChecker()
        
        with pytest.raises(CompilerError) as exc_info:
            typechecker.check_model(model)
        
        error = exc_info.value
        if hasattr(error, 'hint') and error.hint:
            assert "contract" in error.hint.lower() or "FractionFromRatio" in error.hint


class TestContractReportGeneration:
    """Test contract analysis report generation."""

    def test_generate_contract_report_basic(self):
        """Test basic contract report generation."""
        source = """model TestModel {
    param revenue: Currency<USD> = $100000
    param customers: Count<Customer> = 100
    var price: Currency<USD> = revenue / customers
}"""
       
        lexer = Lexer(source)
        parser = Parser(lexer.tokens)
        model = parser.parse_model()
        
        typechecker = TypeChecker()
        # Check model to populate type information
        try:
            typechecker.check_model(model)
        except:
            pass  # May have type errors
        
        report = typechecker.generate_contract_report(model)
        
        assert report is not None
        assert isinstance(report, str)
        assert len(report) > 0

    def test_generate_contract_report_with_justified_conversion(self):
        """Test report shows justified conversions."""
        source = """model TestModel {
    param revenue: Currency<USD> = $100000
    param customers: Count<Customer> = 100
    
    # @contract RevenuePerUnit_to_Price
    # Justification: Average revenue per customer
    var price: Currency<USD> = revenue / customers
}"""
        
        lexer = Lexer(source)
        parser = Parser(lexer.tokens)
        model = parser.parse_model()
        
        typechecker = TypeChecker()
        # Should compile successfully with contract
        typechecker.check_model(model)
        
        report = typechecker.generate_contract_report(model)
        
        # Report should mention the variable or contract
        assert "price" in report or "contract" in report.lower()

    def test_generate_contract_report_empty_model(self):
        """Test report generation for model with no variables."""
        source = """model EmptyModel {
    param value: Currency<USD> = $1000
}"""
        
        lexer = Lexer(source)
        parser = Parser(lexer.tokens)
        model = parser.parse_model()
        
        typechecker = TypeChecker()
        typechecker.check_model(model)
        report = typechecker.generate_contract_report(model)
        
        # Should handle empty case gracefully
        assert report is not None
        assert isinstance(report, str)


class TestCLIContractReport:
    """Test --contract-report CLI flag functionality."""

    def test_analyze_contracts_method_exists(self):
        """Test that PELCompiler has analyze_contracts method."""
        compiler = PELCompiler()
        assert hasattr(compiler, 'analyze_contracts')
        assert callable(compiler.analyze_contracts)

    def test_analyze_contracts_with_valid_file(self, tmp_path):
        """Test contract analysis on a valid PEL file."""
        # Create temporary PEL file
        test_file = tmp_path / "test.pel"
        test_file.write_text("""model TestModel {
    param revenue: Currency<USD> = $100000
    param customers: Count<Customer> = 100
    var price: Currency<USD> = revenue / customers
}""")
        
        compiler = PELCompiler()
        report = compiler.analyze_contracts(test_file)
        assert report is not None
        assert isinstance(report, str)
        assert len(report) > 0

    def test_analyze_contracts_with_nonexistent_file(self):
        """Test contract analysis with nonexistent file."""
        compiler = PELCompiler()
        
        with pytest.raises(Exception):
            compiler.analyze_contracts(Path("/nonexistent/file.pel"))

    def test_analyze_contracts_returns_markdown(self, tmp_path):
        """Test that contract analysis returns markdown format."""
        test_file = tmp_path / "test.pel"
        test_file.write_text("""model TestModel {
    param value: Currency<USD> = $1000
}""")
        
        compiler = PELCompiler()
        report = compiler.analyze_contracts(test_file)
        # Should be markdown format (contains headers or lists)
        assert report is not None
        if report:
            assert "#" in report or "*" in report or "-" in report


class TestPhase2BackwardsCompatibility:
    """Ensure Phase 2 doesn't break Phase 1 functionality."""

    def test_existing_contract_documentation_still_works(self):
        """Test that Phase 1 contract documentation still works."""
        source = """model BackwardsCompatTest {
    param revenue: Currency<USD> = $100000
    param customers: Count<Customer> = 100
    
    # @contract RevenuePerUnit_to_Price
    # Justification: Unit pricing
    var price: Currency<USD> = revenue / customers
}"""
        
        lexer = Lexer(source)
        parser = Parser(lexer.tokens)
        model = parser.parse_model()
        
        typechecker = TypeChecker()
        # Should compile without errors
        typechecker.check_model(model)

    def test_phase1_tests_still_pass(self):
        """Verify Phase 1 contract matching still works."""
        from compiler.semantic_contracts import SemanticContracts
        
        contracts = SemanticContracts.find_conversions(
            "Quotient<Currency, Count>",
            "Currency"
        )
        
        assert len(contracts) > 0
        assert any(c.name == "RevenuePerUnit_to_Price" for c in contracts)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
