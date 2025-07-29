
using System.CommandLine;
using System.CommandLine.Invocation;
using System.Diagnostics;
using System.Text.RegularExpressions;
using Microsoft.Dafny;
using static Microsoft.Dafny.DafnyMain;
using System.Text.Json;
using System.Text.Json.Serialization;

namespace DafnySketcherCli {
  class Program
  {
    static async Task<int> Main(string[] args)
    {
      // define options
      var fileOpt = new System.CommandLine.Option<FileInfo>(new[] { "--file", "-f" }, "Path to your .dfy");
      var sketchOpt = new System.CommandLine.Option<string>(new[] { "--sketch", "-s" }, "Sketch type") { IsRequired = true };
      var methodOpt = new System.CommandLine.Option<string?>(new[] { "--method", "-m" }, "Method name to target");
      var lineOpt = new System.CommandLine.Option<int?>(new[] { "--line", "-l" }, "Single line number to target");
      var rangeOpt = new System.CommandLine.Option<string?>(new[] { "--line-range", "-r" }, "Line range (start-end)");
      var replaceOpt = new System.CommandLine.Option<bool>(new[] { "--replace", "-x" }, "Apply sketch back into file");
      var promptOpt = new System.CommandLine.Option<string?>(new[] { "--prompt", "-p" }, "Optional sketch prompt");

      var root = new RootCommand("Dafny Sketcher CLI")
        { fileOpt, sketchOpt, methodOpt, lineOpt, rangeOpt, replaceOpt, promptOpt };

      root.SetHandler(async (InvocationContext context) =>
      {
        // Retrieve parsed option values
        var file = context.ParseResult.GetValueForOption(fileOpt);
        var sketchType = context.ParseResult.GetValueForOption(sketchOpt);
        var methodName = context.ParseResult.GetValueForOption(methodOpt);
        var line = context.ParseResult.GetValueForOption(lineOpt);
        var range = context.ParseResult.GetValueForOption(rangeOpt);
        var replace = context.ParseResult.GetValueForOption(replaceOpt);
        var prompt = context.ParseResult.GetValueForOption(promptOpt) ?? "";

        var filePath = file?.FullName;
        // Validate inputs
        if (filePath is not null && !File.Exists(filePath))
        {
          await Console.Error.WriteLineAsync($"File not found: {filePath}");
          context.ExitCode = 1;
          return;
        }
        // TODO: Validate that only one of --method, --line, --line-range is set

        var options = DafnyOptions.Default;
        var reporter = new ConsoleErrorReporter(options);

        // Read the source text
        var source = "";
        Microsoft.Dafny.Program? dafnyProgram = null;
        String? dafnyError = null;
        if (filePath is not null)
        {
          source = await File.ReadAllTextAsync(filePath);

          // Parse & resolve using HandleDafnyFile and the new ParseCheck API
          // Load the file through the DafnyMain helper, so it respects search paths, includes, etc.
          var dafnyFile = DafnyFile.HandleDafnyFile(
            OnDiskFileSystem.Instance,
            reporter,
            options,
            new Uri(Path.GetFullPath(filePath)),
            Token.NoToken
          );
          var files = new List<DafnyFile> { dafnyFile };
          var (program, error) = await ParseCheck(
            TextReader.Null,
            files,
            "sketcher-cli",
            options
          );
          dafnyProgram = program;
          dafnyError = error;
        }

        // Figure out your target span
        var method = dafnyProgram is not null && methodName is not null
          ? Utility.GetMethodByName(dafnyProgram, methodName)
          : null;
        int startLine = 0, endLine = 0;
        if (line.HasValue)
        {
          startLine = endLine = line.Value;
        }
        else if (!string.IsNullOrEmpty(range))
        {
          var parts = range!.Split('-');
          startLine = int.Parse(parts[0]);
          endLine = int.Parse(parts[1]);
        }
        else if (method != null)
        {
          startLine = method.Body.StartToken.line;
          endLine = method.Body.EndToken.line - 1;
        }

        // 4) Instantiate the sketcher and fire it
        if (sketchType.StartsWith("errors"))
        {
          var diagnostics = await GetDiagnosticsAsync(filePath, sketchType.Contains("warnings"));
          // 4) Map each error pos into the enclosing Dafny method and print
          var lines = File.ReadAllLines(filePath).ToList();
          foreach (var (ln, col, msg) in diagnostics)
          {
            var m = Utility.GetEnclosingMethodByPosition(
              dafnyProgram, ln, col
            );
            var name = m?.Name ?? "<global>";
            var snippet_line = ln - 1 >= 0 && ln - 1 < lines.Count
              ? lines[ln - 1].Trim()
              : "";
            // e.g., avoid showing lines with only braces
            var snippet = snippet_line.Length > 1 ? " -- in line: " + snippet_line : "";
            Console.WriteLine($"{name}:{ln}:{col} {msg}{snippet}");
          }

        }
        else if (sketchType == "todo")
        {
          var todos = ListTODOs(dafnyProgram);
          var json = JsonSerializer.Serialize(todos);
          await Console.Out.WriteLineAsync(json);
        }
        else if (sketchType == "done")
        {
          var units = ListImplementedUnits(dafnyProgram);
          var json = JsonSerializer.Serialize(units);
          await Console.Out.WriteLineAsync(json);
        }
        else if (sketchType == "todo_lemmas")
        {
          var diagnostics = await GetDiagnosticsAsync(filePath, false /* not warnings, just errors */);
          var all_lemmas = ListAllLemmas(dafnyProgram);
          var error_methods = new HashSet<string>();
          foreach (var (ln, col, msg) in diagnostics)
          {
            var m = Utility.GetEnclosingMethodByPosition(
              dafnyProgram, ln, col
            );
            error_methods.Add(m.Name);
          }
          var todo_lemmas = all_lemmas.Where(x => error_methods.Contains(x.Name)).ToList();
          var json = JsonSerializer.Serialize(todo_lemmas);
          await Console.Out.WriteLineAsync(json);
        }
        else
        {
          var sketcher = ISketcher.Create(sketchType, reporter);
          if (sketcher is null)
          {
            await Console.Error.WriteLineAsync("Error: sketcher unavailable for type " + sketchType);
            context.ExitCode = 1;
            return;
          }

          var req = new SketchRequest(dafnyProgram, source, method, sketchType, startLine, 0/* indent */, prompt);
          var resp = await sketcher.GenerateSketch(req);
          var sketch = resp.Sketch;
          var result = sketch;

          if (replace)
          {
            // 2) Read original lines
            var lines = File.ReadAllLines(filePath).ToList();

            // 3) Compute replace range
            int start = startLine, end = endLine;

            // 4) Replace those lines
            var sketchLines = sketch.Split('\n');
            lines.RemoveRange(start, end - start);
            lines.InsertRange(start, sketchLines);

            // 5) Output
            result = string.Join("\n", lines);
          }

          if (!string.IsNullOrEmpty(dafnyError))
          {
            result = "// " + dafnyError + "\n" + result;
          }

          await Console.Out.WriteLineAsync(result);
        }
        context.ExitCode = 0;
        return;
      });
      return await root.InvokeAsync(args);
    }

    public async static Task<List<(int line, int col, string msg)>> GetDiagnosticsAsync(string filePath, bool includeWarnings)
    {
      // 2) Invoke `dafny verify` normally and capture its text output
      var psi = new ProcessStartInfo("dafny", $"verify \"{filePath}\"")
      {
        RedirectStandardOutput = true,
        RedirectStandardError = true,
        UseShellExecute = false,
      };
      using var proc = Process.Start(psi)!;
      var stdout = await proc.StandardOutput.ReadToEndAsync();
      var stderr = await proc.StandardError.ReadToEndAsync();
      proc.WaitForExit();
      var allText = stdout + "\n" + stderr;

      // 3) Pull out lines like: file.dfy(line,col): Error: message
      var diagnostics = new List<(int line, int col, string msg)>();

      string pattern = $@"\((\d+),(\d+)\):\s*(?:(?:Error:){(includeWarnings ? "|Warning:" : "")})\s*(.*)";
      var regex = new Regex(pattern);
      foreach (var rawLine in allText.Split('\n'))
      {
        if (!rawLine.Contains("Error:") && !(includeWarnings && rawLine.Contains("Warning:")))
        {
          continue;
        }
        var errLine = rawLine.Trim();
        var m = regex.Match(errLine);
        if (m.Success)
        {
          diagnostics.Add((
            int.Parse(m.Groups[1].Value),
            int.Parse(m.Groups[2].Value),
            m.Groups[3].Value
          ));
        }
      }

      // Remove duplicate errors
      diagnostics = diagnostics.Distinct().ToList();
      return diagnostics;
    }
    public static List<Unit> ListTODOs(Microsoft.Dafny.Program dafnyProgram)
    {
      var todos = new List<Unit>();
      if (dafnyProgram.DefaultModuleDef is DefaultModuleDefinition defaultModule)
      {
        foreach (var topLevelDecl in defaultModule.TopLevelDecls)
        {
          if (topLevelDecl is TopLevelDeclWithMembers classDecl)
          {
            foreach (var member in classDecl.Members)
            {
              if (member is MethodOrFunction m)
              {
                string? type = null;
                if (m.HasAxiomAttribute)
                {
                  type = "lemma";
                }
                else if (m is Function f)
                {
                  if (f.Body == null)
                  {
                    type = "function";
                  }
                }
                if (type != null)
                {
                  todos.Add(new Unit
                  {
                    Name = m.Name,
                    startLine = m.StartToken.line,
                    startColumn = m.StartToken.col,
                    InsertLine = m.EndToken.line,
                    InsertColumn = m.EndToken.col,
                    EndLine = m.EndToken.line,
                    EndColumn = m.EndToken.col,
                    Type = type,
                    Status = "todo"
                  });
                }
              }
            }
          }
        }
      }
      return todos;
    }
    public static List<Unit> ListImplementedUnits(Microsoft.Dafny.Program dafnyProgram)
    {
      var units = new List<Unit>();
      if (dafnyProgram.DefaultModuleDef is DefaultModuleDefinition defaultModule)
      {
        foreach (var topLevelDecl in defaultModule.TopLevelDecls)
        {
          if (topLevelDecl is TopLevelDeclWithMembers classDecl)
          {
            foreach (var member in classDecl.Members)
            {
              if (member is MethodOrFunction m)
              {
                string? type = null;
                if (m is Function f)
                {
                  if (f.Body != null)
                  {
                    var isSpec = f.Attributes != null && f.Attributes.Name == "spec";
                    if (!isSpec)
                    {
                      type = "function";
                    }
                  }
                }
                else if (!m.HasAxiomAttribute && m.IsGhost)
                {
                  type = "lemma";
                }
                if (type != null)
                {
                  units.Add(new Unit
                  {
                    Name = m.Name,
                    startLine = m.StartToken.line,
                    startColumn = m.StartToken.col,
                    InsertLine = m.BodyStartTok.line,
                    InsertColumn = m.BodyStartTok.col,
                    EndLine = m.EndToken.line,
                    EndColumn = m.EndToken.col,
                    Type = type,
                    Status = "done"
                  });
                }
              }
            }
          }
        }
      }
      return units;
    }
    public static List<Unit> ListAllLemmas(Microsoft.Dafny.Program dafnyProgram)
    {
      var units = new List<Unit>();
      if (dafnyProgram.DefaultModuleDef is DefaultModuleDefinition defaultModule)
      {
        foreach (var topLevelDecl in defaultModule.TopLevelDecls)
        {
          if (topLevelDecl is TopLevelDeclWithMembers classDecl)
          {
            foreach (var member in classDecl.Members)
            {
              if (member is MethodOrFunction m)
              {
                if (m.IsGhost)
                {
                  units.Add(new Unit
                  {
                    Name = m.Name,
                    startLine = m.StartToken.line,
                    startColumn = m.StartToken.col,
                    InsertLine = m.BodyStartTok.line,
                    InsertColumn = m.BodyStartTok.col,
                    EndLine = m.EndToken.line,
                    EndColumn = m.EndToken.col,
                    Type = "lemma",
                    Status = "any"
                  });
                }
              }
            }
          }
        }
      }
      return units;
    }
  }
  public class Unit
  {
    [JsonPropertyName("name")]
    required public string Name { get; set; }
    [JsonPropertyName("startLine")]
    required public int startLine { get; set; }
    [JsonPropertyName("startColumn")]
    required public int startColumn { get; set; }
    [JsonPropertyName("insertLine")]
    required public int InsertLine { get; set; }
    [JsonPropertyName("insertColumn")]
    required public int InsertColumn { get; set; }
    [JsonPropertyName("endLine")]
    required public int EndLine { get; set; }

    [JsonPropertyName("endColumn")]
    required public int EndColumn { get; set; }
    [JsonPropertyName("type")]
    required public string Type { get; set; }
    [JsonPropertyName("status")]
    required public string Status { get; set; }
  }
}