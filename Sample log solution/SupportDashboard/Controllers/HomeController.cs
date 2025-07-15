using Microsoft.AspNetCore.Mvc;
using SupportDashboard.Models;
using SupportDashboard.Services;

namespace SupportDashboard.Controllers
{
    public class HomeController : Controller
    {
        private readonly TicketService _ticketService;

        public HomeController(TicketService ticketService)
        {
            Serilog.Log.Information("HomeController created");
            _ticketService = ticketService;
        }

        public IActionResult Index()
        {
            var tickets = _ticketService.GetAll();
            Serilog.Log.Information("Tickets count at Index: {Count}", tickets.Count);
            return View(tickets);
        }

        [HttpPost]
        public IActionResult Create(string title, string description, string urgency)
        {
            var newTicket = new Ticket
            {
                Id = _ticketService.GetAll().Count + 1,
                Title = title,
                Description = description,
                Urgency = urgency,
                Status = "New"
            };

            _ticketService.Add(newTicket);
            Serilog.Log.Information("Ticket #{Id} created: {Title}", newTicket.Id, newTicket.Title);
            return RedirectToAction("Index");
        }

        [HttpPost]
        public IActionResult Accept(int id)
        {
            var ticket = _ticketService.GetById(id);
            if (ticket != null)
            {
                ticket.Status = "Accepted";
                Serilog.Log.Information("Ticket #{Id} accepted", id);

                Serilog.Log.Error("Simulated error: Dependency resolution failed: Service 'ITicketRepository' could not be instantiated due to circular dependency on 'ILogger<TicketRepository>'. Check DI configuration and nested resolution paths.");
            }
            return RedirectToAction("Index");
        }

        [HttpPost]
        public IActionResult Resolve(int id)
        {
            var ticket = _ticketService.GetById(id);
            if (ticket != null)
            {
                ticket.Status = "Resolved";
                Serilog.Log.Information("Ticket #{Id} resolved", id);
            }
            return RedirectToAction("Index");
        }

        [HttpPost]
        public IActionResult Escalate(int id)
        {
            var ticket = _ticketService.GetById(id);
            if (ticket != null)
            {
                ticket.Status = "Escalated";
                Serilog.Log.Error("Ticket #{Id} escalated due to critical issue", id);
            }
            return RedirectToAction("Index");
        }
    }
}
