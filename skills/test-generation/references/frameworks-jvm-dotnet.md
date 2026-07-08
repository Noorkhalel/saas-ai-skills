# JVM and .NET Testing: JUnit 5, xUnit, NUnit

## JUnit 5

### Test Structure

```java
import org.junit.jupiter.api.*;
import static org.junit.jupiter.api.Assertions.*;

class DiscountCalculatorTest {

    private DiscountCalculator calculator;

    @BeforeEach
    void setUp() {
        calculator = new DiscountCalculator();
    }

    @Test
    @DisplayName("Gold tier applies 20% discount")
    void goldTierAppliesTwentyPercentDiscount() {
        // Arrange
        double price = 100.0;

        // Act
        double discount = calculator.calculate(price, Tier.GOLD);

        // Assert
        assertEquals(20.0, discount, 0.001);
    }

    @Test
    @DisplayName("Throws IllegalArgumentException for null tier")
    void throwsForNullTier() {
        assertThrows(IllegalArgumentException.class,
            () -> calculator.calculate(100.0, null));
    }
}
```

### Parameterized Tests

```java
import org.junit.jupiter.params.ParameterizedTest;
import org.junit.jupiter.params.provider.*;

class DiscountCalculatorTest {

    @ParameterizedTest(name = "{0} tier at ${1} → ${2} discount")
    @CsvSource({
        "BRONZE, 100.0, 5.0",
        "SILVER, 100.0, 10.0",
        "GOLD,   100.0, 20.0",
        "GOLD,   0.0,   0.0",
    })
    void discountByTier(Tier tier, double price, double expectedDiscount) {
        double result = calculator.calculate(price, tier);
        assertEquals(expectedDiscount, result, 0.001);
    }

    @ParameterizedTest
    @MethodSource("edgeCasePrices")
    void handlesEdgeCasePrices(double price, Tier tier, double expected) {
        assertEquals(expected, calculator.calculate(price, tier), 0.001);
    }

    static Stream<Arguments> edgeCasePrices() {
        return Stream.of(
            Arguments.of(0.0, Tier.GOLD, 0.0),
            Arguments.of(0.01, Tier.BRONZE, 0.0005),
            Arguments.of(999999.99, Tier.GOLD, 199999.998)
        );
    }
}
```

### Lifecycle

```java
@TestInstance(TestInstance.Lifecycle.PER_CLASS) // Share instance across tests in class
class ExpensiveResourceTest {

    private Database db;

    @BeforeAll
    void setUpDatabase() {
        db = Database.createTestInstance();
    }

    @AfterAll
    void tearDownDatabase() {
        db.close();
    }

    @BeforeEach
    void cleanState() {
        db.truncateAll();
    }
}
```

### Nested Tests

```java
@DisplayName("UserService")
class UserServiceTest {

    @Nested
    @DisplayName("when creating a user")
    class WhenCreatingUser {

        @Test
        @DisplayName("saves user with generated ID")
        void savesUserWithGeneratedId() { /* ... */ }

        @Test
        @DisplayName("rejects duplicate email")
        void rejectsDuplicateEmail() { /* ... */ }
    }

    @Nested
    @DisplayName("when deleting a user")
    class WhenDeletingUser {

        @Test
        @DisplayName("removes user from database")
        void removesFromDatabase() { /* ... */ }
    }
}
```

### Assertions

```java
// Basic
assertEquals(expected, actual);
assertTrue(condition);
assertNotNull(object);

// Exception
assertThrows(IllegalArgumentException.class, () -> service.process(null));

// Multiple assertions (all run even if one fails)
assertAll("user properties",
    () -> assertEquals("John", user.getName()),
    () -> assertEquals("john@example.com", user.getEmail()),
    () -> assertNotNull(user.getId())
);

// Timeout
assertTimeout(Duration.ofSeconds(2), () -> service.processLargeFile(file));
```

## xUnit (.NET)

### Test Structure

```csharp
public class DiscountCalculatorTests
{
    private readonly DiscountCalculator _calculator = new();

    [Fact]
    public void Calculate_GoldTier_AppliesTwentyPercent()
    {
        // Arrange
        var price = 100m;

        // Act
        var discount = _calculator.Calculate(price, Tier.Gold);

        // Assert
        Assert.Equal(20m, discount);
    }

    [Fact]
    public void Calculate_NullTier_ThrowsArgumentException()
    {
        Assert.Throws<ArgumentNullException>(
            () => _calculator.Calculate(100m, null!));
    }
}
```

### Theories (Parameterized Tests)

```csharp
public class DiscountCalculatorTests
{
    [Theory]
    [InlineData(Tier.Bronze, 100, 5)]
    [InlineData(Tier.Silver, 100, 10)]
    [InlineData(Tier.Gold, 100, 20)]
    public void Calculate_ReturnsCorrectDiscount(Tier tier, decimal price, decimal expected)
    {
        var result = _calculator.Calculate(price, tier);
        Assert.Equal(expected, result);
    }

    [Theory]
    [MemberData(nameof(EdgeCaseData))]
    public void Calculate_HandlesEdgeCases(decimal price, Tier tier, decimal expected)
    {
        Assert.Equal(expected, _calculator.Calculate(price, tier));
    }

    public static IEnumerable<object[]> EdgeCaseData =>
        new List<object[]>
        {
            new object[] { 0m, Tier.Gold, 0m },
            new object[] { 0.01m, Tier.Bronze, 0.0005m },
        };
}
```

### Fixture Injection (Constructor DI)

```csharp
// xUnit creates a new instance per test (clean state)
public class UserServiceTests : IDisposable
{
    private readonly TestDatabase _db;
    private readonly UserService _service;

    public UserServiceTests()
    {
        _db = new TestDatabase();
        _service = new UserService(_db.Context);
    }

    public void Dispose()
    {
        _db.Dispose();
    }

    [Fact]
    public void CreateUser_ValidInput_ReturnsCreatedUser()
    {
        var user = _service.Create("test@example.com", "Test User");
        Assert.NotNull(user.Id);
        Assert.Equal("test@example.com", user.Email);
    }
}
```

### Collection Fixtures (Shared Expensive Resources)

```csharp
// Shared across all tests in the collection
[CollectionDefinition("Database")]
public class DatabaseCollection : ICollectionFixture<DatabaseFixture> { }

public class DatabaseFixture : IAsyncLifetime
{
    public TestDbContext Context { get; private set; } = null!;

    public async Task InitializeAsync()
    {
        Context = await TestDbContext.CreateAsync();
    }

    public async Task DisposeAsync()
    {
        await Context.DisposeAsync();
    }
}

[Collection("Database")]
public class UserServiceTests
{
    private readonly DatabaseFixture _fixture;

    public UserServiceTests(DatabaseFixture fixture)
    {
        _fixture = fixture;
    }
}
```

## NUnit

### Test Structure

```csharp
[TestFixture]
public class DiscountCalculatorTests
{
    private DiscountCalculator _calculator;

    [SetUp]
    public void SetUp()
    {
        _calculator = new DiscountCalculator();
    }

    [Test]
    public void Calculate_GoldTier_AppliesTwentyPercent()
    {
        var result = _calculator.Calculate(100m, Tier.Gold);
        Assert.That(result, Is.EqualTo(20m));
    }

    [TestCase(Tier.Bronze, 100, 5)]
    [TestCase(Tier.Silver, 100, 10)]
    [TestCase(Tier.Gold, 100, 20)]
    public void Calculate_ReturnsCorrectDiscount(Tier tier, decimal price, decimal expected)
    {
        var result = _calculator.Calculate(price, tier);
        Assert.That(result, Is.EqualTo(expected));
    }

    [Test]
    public void Calculate_NegativePrice_ThrowsArgumentException()
    {
        Assert.That(
            () => _calculator.Calculate(-1m, Tier.Gold),
            Throws.TypeOf<ArgumentOutOfRangeException>());
    }
}
```

### NUnit Constraint Model

```csharp
// Prefer Assert.That with constraints over classic Assert.AreEqual
Assert.That(result, Is.EqualTo(expected));
Assert.That(result, Is.GreaterThan(0));
Assert.That(collection, Has.Count.EqualTo(3));
Assert.That(collection, Does.Contain(item));
Assert.That(result, Is.EqualTo(1.999).Within(0.01));
Assert.That(text, Does.StartWith("Error:"));
```
